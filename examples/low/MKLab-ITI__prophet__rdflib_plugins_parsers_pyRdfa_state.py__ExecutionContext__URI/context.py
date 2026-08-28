# Context shim (see meta.json): the module-level bindings of
# rdflib/plugins/parsers/pyRdfa/state.py and pyRdfa/__init__.py that the
# extracted region needs, so it can execute outside the package.  Used
# IDENTICALLY by original.py and translated.ldpy.
# Provenance: MKLab-ITI/prophet@eee2ab51de (a vendored copy of Ivan Herman's
# pyRdfa, W3C software licence -- see meta.json).
import sys

# state.py, module level
(py_v_major, py_v_minor, py_v_micro, py_v_final, py_v_serial) = sys.version_info

# pyRdfa/__init__.py, module level
err_URI_scheme = "Unusual URI scheme used in <%s>; may that be a mistake, e.g., resulting from using an undefined CURIE prefix or an incorrect CURIE?"

registered_iana_schemes = [
	"aaa","aaas","acap","cap","cid","crid","data","dav","dict","dns","fax","file", "ftp","geo","go",
	"gopher","h323","http","https","iax","icap","im","imap","info","ipp","iris","ldap", "lsid",
	"mailto","mid","modem","msrp","msrps", "mtqp", "mupdate","news","nfs","nntp","opaquelocktoken",
	"pop","pres", "prospero","rstp","rsync", "service","shttp","sieve","sip","sips", "sms", "snmp", "soap", "tag",
	"tel","telnet", "tftp", "thismessage","tn3270","tip","tv","urn","vemmi","wais","ws", "wss", "xmpp"
]

unofficial_common = [
	"about", "adiumxtra", "aim", "apt", "afp", "aw", "bitcoin", "bolo", "callto", "chrome", "coap",
	"content", "cvs", "doi", "ed2k", "facetime", "feed", "finger", "fish", "git", "gg",
	"gizmoproject", "gtalk", "irc", "ircs", "irc6", "itms", "jar", "javascript",
	"keyparc", "lastfm", "ldaps", "magnet", "maps", "market", "message", "mms",
	"msnim", "mumble", "mvn", "notes", "palm", "paparazzi", "psync", "rmi",
	"secondlife", "sgn", "skype", "spotify", "ssh", "sftp", "smb", "soldat",
	"steam", "svn", "teamspeak", "things", "udb", "unreal", "ut2004",
	"ventrillo", "view-source", "webcal", "wtai", "wyciwyg", "xfire", "xri", "ymsgr"
]

historical_iana_schemes = [
	"fax", "mailserver", "modem", "pack", "prospero", "snews", "videotex", "wais"
]

provisional_iana_schemes = [
	"afs", "dtn", "dvb", "icon", "ipn", "jms", "oid", "rsync", "ni"
]

other_used_schemes = [
	"hdl", "isbn", "issn", "mstp", "rtmp", "rtspu", "stp"
]

uri_schemes = registered_iana_schemes + unofficial_common + historical_iana_schemes + provisional_iana_schemes + other_used_schemes
