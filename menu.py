#a module to create menus
from functools import reduce

def make(all_headings, all_contents, all_widths=None):
    '''|bot|
    (list of str, list of list of str, list of int) -> str

    EXANPLE:
    make(['action', 'cost'], [['feed treat', 'feed pudding', 'tuck into bed', 'read story', 'hug', 'pat'], ['50', '100', '25', '30', '200', '300']], [15, 6])

    RESULT
             options |    action     | cost
            ---------+---------------+------
                1    |  feed treat   |  50
                2    | feed pudding  | 100
                3    | tuck into bed |  25
                4    |  read story   |  30
                5    |      hug      | 200
                6    |      pat      | 300

   '''
    #---decide widths
    if not all_widths:
        all_widths = []
        index = 0
        for column in all_contents:
            longest_content_length = reduce(max, (len(e) for e in column))
            heading_length = len(all_headings[index])
            if longest_content_length < heading_length:
                longest_length = heading_length
            else:
                longest_length = longest_content_length
            all_widths.append(longest_length + 2) #extra 2 for padding

    #---grab number of cols and rows
    number_of_cols = len(all_headings) + 1 #because we will insert numbers column
    number_of_rows = len(all_contents[0])

    #---generate numbers
    all_numbers = list(num for num in range(1, number_of_rows+1))
    first_col_name = 'options'
    all_headings.insert(0, first_col_name)
    all_contents.insert(0, all_numbers)
    all_widths.insert(0, len(first_col_name) + 2)

    #---make heading
    heading = ''
    index = 0
    for h in all_headings:
        heading += f'{h:^{all_widths[index]}}|'
        index += 1
    heading = heading[:-1] #remove final |
    heading += '\n'
    
    #---make border
    border = ''
    for w in all_widths:
        border += f"{'-' * w}+"
    border = border[:-1] #remove final +
    border += '\n'

    #---make contents
    contents = ''
    ac = all_contents
    for index in range(number_of_rows):
        w_index = 0
        row = ''
        for column in all_contents:
            content = column[index]
            width = all_widths[w_index]
            row += f"{content:^{width}}|"
            w_index += 1
        row = row[:-1] #remove final |
        row += '\n'
        contents += row

    menu = heading + border + contents
    return menu

if __name__ == '__main__':
    call = make(['action', 'cost'], [['feed treat', 'feed pudding', 'tuck into bed', 'read story', 'hug', 'pat'], ['50', '100', '25', '30', '200', '300']])
    print(call)
