#!/bin/bash

set -euo pipefail
shopt -s inherit_errexit

export \
	DEBIAN_FRONTEND="noninteractive" \
	DEBIAN_PRIORITY="critical" \
	NEEDRESTART_SUSPEND="1"

. /var/lib/vultr/common.sh

########
echo "Setting variables"
########
cockpit_port="9080"
php_version="8.1"  # php8.2-mcrypt (phpmyadmin dep) seems to not be present in upstream repo, sticking with 8.1 for now

metadata_variable_list=(
	"pmadbpass"
	"pmadbuser"
	"pmamodalpass"
	"wpadminpass"
	"wpadminuser"
	"xhprofpass"
	"xhprofuser"
)





wpadminemail="admin@gmail.com"
wptitle="Vultr WordPress"

echo "wpadminemail is ${wpadminemail}"
wp_plugin_list=(
	"wordfence"
    "all-in-one-wp-migration"
)

if [[ -e /opt/vultr/woocommerce ]]; then
	wp_plugin_list+=("woocommerce")
	rm -f /opt/vultr/woocommerce
fi

########
echo "Retrieve necessary metadata values"
########

get_ip
get_var_opt "mysql_ibps"
get_var_opt "mysql_toc"


for var in "${metadata_variable_list[@]}"; do
	get_var "${var}"
    echo "${var} is ${!var}"
done

# Exit if any required variables are not set
: "${ip:?}" \
	"${pmadbpass:?}" "${pmadbuser:?}" "${pmamodalpass:?}" \
	"${wpadminemail:?}" "${wpadminpass:?}" "${wpadminuser:?}" "${wptitle:?}" \
	"${xhprofpass:?}" "${xhprofuser:?}"

########
echo "Download WordPress CLI utility 'wp-cli'"
########
curl --silent --output /usr/local/bin/wp-cli "https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar"
chown www-data:www-data /usr/local/bin/wp-cli
chmod +x /usr/local/bin/wp-cli

########
echo "Disable unattended upgrades while configuring app"
########
toggle_unattended_upgrades "disable"

########
echo "Install and configure SQL Database"
########
install_mysql "${mysql_ibps:-"0"}" "${mysql_toc:-"0"}"
systemctl enable --now mariadb.service

########
echo "Install and configure PHP"
########
install_php "${php_version}" "optimize"

########
echo "Install and configure nginx"
########
install_nginx

########
echo "Install 'certbot'"
########
install_certbot

########
echo "Install, configure, and secure XHProf"
########
install_xhprof "${ip}"
htpasswd -B -i -c /etc/nginx/htpasswd/xhprof "xhprofuser${xhprofuser}" <<< "${xhprofpass}"

########
echo "Install, configure, and secure PHPMyAdmin"
########
install_phpmyadmin "pmauser${pmadbuser}" "${pmadbpass}"
htpasswd -B -i -c /etc/nginx/htpasswd/phpmyadmin "pmauser${pmadbuser}" <<< "${pmamodalpass}"

########
echo "Generate TLS certificates"
########
generate_self_signed_cert

########
echo "Install and configure Cockpit"
########
install_cockpit "${ip}" "${cockpit_port}"

########
echo "Install and configure 'maldet'"
########
install_maldet
systemctl enable maldet.service

########
echo "Install and configure WordPress"
########
mkdir -p /etc/nginx/orig
mv /root/app_binaries/wordpress_http{,s}.conf /etc/nginx/orig/
cp /etc/nginx/orig/wordpress_http{,s}.conf /etc/nginx/conf.d/

(
	cd /var/www/html
	curl --silent --output latest.zip "https://wordpress.org/latest.zip"

	unzip -qq latest.zip
	rm -f latest.zip

	mv wordpress/* .
	rmdir wordpress
)
mkdir -p /root/wp-sensitive-files /var/www/html/wp-content/uploads
mv /var/www/html/license.txt /var/www/html/readme.html /root/wp-sensitive-files/

rm -rf \
	/var/www/html/wp-config-sample.php \
	/var/www/html/wp-content/plugins/akismet \
	/var/www/html/wp-content/plugins/hello.php

chmod 755 /var/www/html/wp-content/uploads
chown -R www-data:www-data /var/www

########
echo "Configure WordPress database"
########
wp_db_name="wp$(generate_random_characters 7 digit)"
wp_db_user="wpuser$(generate_random_characters 5 digit)"
wp_db_pass="$(generate_db_password)"
mysql --defaults-file=/root/.my.cnf -u root -e "CREATE DATABASE ${wp_db_name};"
mysql --defaults-file=/root/.my.cnf -u root -e "CREATE USER '${wp_db_user}'@'localhost' IDENTIFIED BY '${wp_db_pass}';"
mysql --defaults-file=/root/.my.cnf -u root \
	-e "GRANT ALL PRIVILEGES ON ${wp_db_name}.* TO '${wp_db_user}'@'localhost'; FLUSH PRIVILEGES;"

########
echo "Create WordPress configuration"
########
/usr/local/bin/wp config create \
	--dbname="${wp_db_name}" \
	--dbuser="${wp_db_user}" \
	--dbpass="${wp_db_pass}" \
	--extra-php << EXTRAPHP
define( 'FORCE_SSL_ADMIN', false );
define( 'FS_METHOD' , 'direct' );
if (! defined('WFWAF_STORAGE_ENGINE')) { define('WFWAF_STORAGE_ENGINE', 'mysqli'); }
EXTRAPHP

########
echo "Complete installation of WordPress via 'wp-cli'"
########
/usr/local/bin/wp core install \
	--url="${ip}" \
	--title="${wptitle}" \
	--admin_user="wpauser${wpadminuser}" \
	--admin_password="${wpadminpass}" \
	--admin_email="${wpadminemail}" \
	--skip-email

########
echo "Update wp-cli"
########
/usr/local/bin/wp-cli cli update

########
echo "Wait for completion of a successful WordPress installation"
########
until /usr/local/bin/wp &> /dev/null; do
	sleep 1
done

########
echo "Install WordPress plugins"
########
/usr/local/bin/wp plugin install "${wp_plugin_list[@]}" --activate

for plugin in "${wp_plugin_list[@]}"; do
	[[ -d "/var/www/html/wp-content/plugins/${plugin}" ]] ||
		{
			printf 'Plugin (%s) not installed!\n' "${plugin}"
			return 255
		}
	printf 'Plugin (%s) installed and activated!\n' "${plugin}"
done

# add file .wpress ai1wm_import


########
echo "Check for WordPress updates"
########
/usr/local/bin/wp core update

########
echo "Ensure correct permissions on web content files"
########
chown -R www-data:www-data /var/www/html/

autoremove_packages

########
echo "Re-enable unattended upgrades as app is configured"
########
toggle_unattended_upgrades "enable"
cleanup_imageless

########
echo "Enable services"
########
systemctl enable \
	cockpit.socket \
	"php${php_version}-fpm.service" \
	nginx.service

########
echo "Configure firewall"
########
ufw default deny incoming
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow "${cockpit_port}/tcp"
ufw status verbose

########
echo "Reboot to ensure the kernel, all services, and libraries are as up to date as possible"
########
touch /var/lib/vultr/states/.reboot
reboot now || exit 0

