# --------------------------------------------------------------------------------
# Split Wordpress XML (using Element Tree)
# --------------------------------------------------------------------------------

import xml.etree.ElementTree as ET
xmldata = 'input/dmclubcustomerblog.wordpress.2014-10-29.xml'

depth = 0
prefix_width = 8
prefix_dots = '.' * prefix_width
line_template = '{prefix:<0.{prefix_len}}{event:<8}{suffix:<{suffix_len}} {node.tag:<12} {node_id}'

for (event, node) in ET.iterparse(xmldata, ['start', 'end', 'start-ns', 'end-ns']):
    if event == 'end':
        depth -= 1

    prefix_len = depth * 2
    
    print line_template.format(prefix=prefix_dots,
                               prefix_len=prefix_len,
                               suffix='',
                               suffix_len=(prefix_width - prefix_len),
                               node=node,
                               node_id=id(node),
                               event=event,
                               )
    
    if event == 'start':
        depth += 1
