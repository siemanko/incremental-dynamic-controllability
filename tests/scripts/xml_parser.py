import gflags
import xml.etree.ElementTree as ET
import sys

gflags.DEFINE_string('input_file', None, 'XML file to convert')
gflags.MarkFlagAsRequired('input_file')
gflags.DEFINE_enum('output_type', 'summary', ['summary', 'dot'], 'Type of output to convert the file to')

FLAGS = gflags.FLAGS

def get_node_renaming(edge_list):
    names = set()

    def num_to_name(num):
        assert num >= 1
        result = []
        while num > 0:
            result.append(num%26)
            num /= 26
        for i in xrange(len(result)):
            if result[i] <= 0 and i+1 < len(result):
                result[i]+=26
                result[i+1]-=1
        if result[-1] == 0:
            result = result[:-1]
        result.reverse()
        return ''.join([chr(ord('A') + x-1) for x in result])

    for start, end, _, _, _ in edge_list:
        names.add(start)
        names.add(end)
    renaming = {}
    next_number = 1
    for name in names:
        renaming[name] = num_to_name(next_number)
        next_number += 1
    return renaming

def generate_graphviz(edge_list):
    renaming = get_node_renaming(edge_list)
    print "digraph G {"
    print "rankdir=\"LR\";"
    for start, end, lb, ub, etype in edge_list:
        edge_style = 'dotted' if etype == 'Uncontrollable' else 'solid'
        lb = '%.2f' % (float(lb))
        ub = '%.2f' % (float(ub),)
        print "%s -> %s [label=\"[%s, %s]\", style=%s];" % (renaming[start],
                                                            renaming[end],
                                                            lb,
                                                            ub,
                                                            edge_style)
    print "}"

def summary(edge_list):
    print 'Number of nodes: %d' % len(get_node_renaming(edge_list))
    print 'Number of edges: %d' % len(edge_list)
    print '    of which'
    controllable = len([e for e in edge_list if e[4] == 'Controllable'])
    print '        controllable: %d' % controllable
    print '        Uncontrollable: %d' % (len(edge_list) - controllable,)

def main():
    argv = FLAGS(sys.argv)
    #print 'Parsing %s' % (FLAGS.input_file,)
    tree = ET.parse(FLAGS.input_file)
    edge_list = []
    for constraint in tree.getroot().findall('CONSTRAINT'):        
        edge_list.append((constraint.find('START').text,
                          constraint.find('END').text,
                          constraint.find('LOWERBOUND').text,
                          constraint.find('UPPERBOUND').text,
                          constraint.find('TYPE').text.split(';')[0],))
    if FLAGS.output_type == 'dot':
        generate_graphviz(edge_list)
    if FLAGS.output_type == 'summary':
        summary(edge_list)

if __name__ == '__main__':
    main()