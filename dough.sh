cd /root
git clone https://github.com/sunxin3/dough.git

cd /usr/lib/python2.6/site-packages/horizon/dashboards/nova
mv dashboard.py dashboard.py.bak_geyg
cp /root/nova/dashboard.py ./
cp -rf /root/nova/dough ./

cd /etc
mkdir dough
cd dough
cp /root/dough.conf ./

cd /usr/lib/python2.6/site-packages
mv dough-0.1.1-py2.6.egg dough-0.1.1-py2.6.egg.bak.geyg
cp -rf /root/dough-0.1.1-py2.6.egg ./



service httpd restart
