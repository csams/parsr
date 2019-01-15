from parsr.logrotate_conf import loads

EXAMPLE = """
# sample logrotate configuration file
compress

/var/log/messages {
    rotate 5
    weekly
    postrotate
        /usr/bin/killall -HUP syslogd
    endscript
}

"/var/log/httpd/access.log" /var/log/httpd/error.log {
    rotate 5
    mail www@my.org
    size 100k
    sharedscripts
    postrotate
        /usr/bin/killall -HUP httpd
    endscript
}

/var/log/news/* {
    monthly
    rotate 2
    olddir /var/log/news/old
    missingok
    postrotate
        kill -HUP 'cat /var/run/inn.pid'
    endscript
    nocompress
}
""".strip()


SIMPLE = """
# sample logrotate configuration file
compress

 /var/log/messages {
    rotate 5
    weekly
    postrotate
        /usr/bin/killall -HUP syslogd
    endscript
}
"""


def test_logrotate_simple():
    res = loads(SIMPLE)
    assert "compress" in res
    assert "/var/log/messages" in res


def test_logrotate_example():
    res = loads(EXAMPLE)
    assert res["compress"] is None
    assert res["/var/log/messages"]["rotate"] == 5
    assert res["/var/log/messages"]["weekly"] is None
    assert res["/var/log/messages"]["postrotate"] == "/usr/bin/killall -HUP syslogd"


def xtest_logrotate_multikey():
    res = loads(EXAMPLE)
    assert res["compress"] is None
    assert res["/var/log/httpd/access.log"]["rotate"] == 5
    assert res["/var/log/httpd/access.log"]["size"] == "100k"
    assert res["/var/log/httpd/access.log"]["sharedscripts"] is None

    assert res["/var/log/httpd/error.log"]["rotate"] == 5
    assert res["/var/log/httpd/error.log"]["size"] == "100k"
    assert res["/var/log/httpd/error.log"]["sharedscripts"] is None
    assert res["/var/log/news/*"]["postrotate"] == "kill -HUP 'cat /var/run/inn.pid'"
