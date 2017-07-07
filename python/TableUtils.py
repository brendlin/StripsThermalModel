
#
# A "list of rows"
#
def PrintLatexTable(thing,justs=[]) :

    #
    # Get the max column width
    #
    max_column_width = []
    for i,x in enumerate(thing) :
        for j,y in enumerate(x) :
            y = y.replace('%','\\%')
            y = y.replace('\t','\\t')
            if '$' not in y :
                y = y.replace('_','\_')
            if i == 0 :
                max_column_width.append(len(y))
            else :
                if len(max_column_width) < j + 1 :
                    print 'Error in PrintLatexTable - column widths are not the same.'
                    import sys; sys.exit()
                max_column_width[j] = max(max_column_width[j],len(y))

    #
    # Fill in the text
    #
    text = ''
    justs_text = ['']*len(thing[0])
    for i,x in enumerate(thing) :
        for j,y in enumerate(x) :
            # justification
            just = 'rjust'
            if j == 0 :
                just = 'ljust'
            if j < len(justs) :
                just = justs[j].replace('l','ljust').replace('r','rjust')
            justs_text[j] = just.replace('ljust','l').replace('rjust','r')

            y = y.replace('%','\\%')
            y = y.replace('\t','\\t')
            if '$' not in y :
                y = y.replace('_','\_')
            if j == len(x)-1 :
                hline = '' if i else '\\hline'
                text += '%s \\\\ %s\n'%(getattr(y,just)(max_column_width[j]),hline)
            elif j == 0 :
                text += '%s & '%(getattr(y,just)(max_column_width[j]))
            else :
                text += '%s & '%(getattr(y,just)(max_column_width[j]))
                
    justs_text = '|'.join(justs_text)
    text = '\\begin{tabular}{|%s|} \hline \n'%(justs_text) + text
    text += '\hline\end{tabular}\n'
    return text

