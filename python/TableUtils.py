
#
# A "list of rows"
#
def PrintLatexTable(thing,justs=[],nsigfig=3) :

    #
    # Calculate the correct number of digits, given that you want at least
    # 3 sig figs for the smallest number.
    # Requires floats to be passed, not strings.
    #
    ndecimalplaces = 0
    for i,x in enumerate(thing) :
        for j,y in enumerate(x) :
            if type(y) != type(0.1) :
                continue

            result = '%.*g'%(nsigfig,y)
            if '.' not in result :
                ndecimalplaces = max(0,ndecimalplaces)
            else :
                ndecimalplaces = max(len(result.split('.')[-1]),ndecimalplaces)

    for i,x in enumerate(thing) :
        for j,y in enumerate(x) :
            if type(y) != type(0.1) :
                continue
            try :
                thing[i][j] = '%.*f'%(ndecimalplaces,thing[i][j])
            except :
                pass

    #
    # Text replacements for latex table.
    #
    def MakeTextReplacements(entry) :
        entry = entry.replace('%','\\%')
        entry = entry.replace('\t','\\t')
        if '$' not in entry :
            entry = entry.replace('_','\_')
        return entry

    #
    # Get the max column width
    #
    max_column_width = []
    for i,x in enumerate(thing) :
        for j,y in enumerate(x) :
            y = MakeTextReplacements(y)
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

            y = MakeTextReplacements(y)
            if j == len(x)-1 :
                hline = '' if i else '\\hline'
                text += '%s \\\\ %s\n'%(getattr(y,just)(max_column_width[j]),hline)
            elif j == 0 :
                text += '%s & '%(getattr(y,just)(max_column_width[j]))
            else :
                text += '%s & '%(getattr(y,just)(max_column_width[j]))
                
    justs_text = '|'.join(justs_text)

    ret_text =  '\\begin{table}[ht]\n'
    ret_text += '\\adjustbox{max width=\\textwidth}{ %% just before tabular\n'
    ret_text += '\\begin{tabular}{|%s|} \hline %% data_below\n'%(justs_text) + text
    ret_text += '\hline\end{tabular}\n'
    ret_text += '} %% resize box after tabular\n'
    ret_text +=  '\\end{table}\n'
    return ret_text

