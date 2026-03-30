"""
There are dates that are not precise and use qualifiers to get a greater range of 
- dates with 4 digits
- has question marks?
- has 'ca' (circa)?
- has 'fl' (flourished)?
- has 'fl' and 'ca'?
- has 'fl' and 'entre' (portuguese for 'between')?

The QIDs for the qualifiers are:
circa = Q5727902



"""

import re


# dates = 'ca entre 1970-fl 2050'


global f 
f = open(f'datas.csv', 'w')


qualifiers_qids = {'ca': 'Q5727902', 'fl': {'property': 'P1317)'}}


def get_dates(record, dates):
    dates_dict = {}
    # birth_date = 0
    # death_date = 0
    # floruit_birth_date = ""
    # floruit_death_date = ""
    # circa_birth_date = ""
    # circa_death_date = ""
    qualifiers_dict = {}

    dates_dict = get_dates_dict(dates)
    print("dates: ", dates_dict)

    # a.c. 
    # qualifiers = get_qualifiers_dict(record, dates_dict, dates, 'ca|fl|\?|(a.c.)|([-]+)', ['ca', 'fl'])
    qualifiers_dict = get_qualifiers_dict(record, dates_dict, dates, r'(ca|fl|dps|post\s\d{3,4}|ca|dps|post\s-)', ['ca', 'fl'])
    # print("******************************************qualifiers: ", qualifiers_dict)


    
    # if len(qualifiers) > 0:
    #     if 'ca' in qualifiers['birth_date']:
    #         qualifiers_result['circa_birth_date'] = 'ca'
    #     else:
    #         qualifiers_result['circa_birth_date'] = ''
        
    #     if 'ca' in qualifiers['death_date']:
    #         qualifiers_result['circa_death_date'] = 'ca'
    #     else:
    #         qualifiers_result['circa_death_date'] = ''
            
    #     if 'fl' in qualifiers['birth_date'] and dates_dict['birth_date'] > 0:
            
    #         qualifiers_result['floruit_birth_date'] = int(dates_dict['birth_date'])
    #     else:
    #         qualifiers_result['floruit_birth_date'] = 0

    #     if 'fl' in qualifiers['death_date'] and dates_dict['death_date'] > 0:
    #         qualifiers_result['floruit_death_date'] = int(dates_dict['death_date'])
    #     else:
    #         qualifiers_result['floruit_death_date'] = 0

    return dates_dict, qualifiers_dict
        # "birth_date": birth_date,
        # "death_date": death_date,
        # "floruit_birth_date": floruit_birth_date,
        # "floruit_death_date": floruit_death_date,
        # "circa_birth_date": circa_birth_date,
        # "circa_death_date": circa_death_date       
    
    
    # birth_date = 0
    # death_date = 0

    # try:
    #     dates = re.findall('([0-9]{4})-([0-9]{4})', date)
    # except:
    #     return '', ''
    
    # try:
    #     birth_date = int(dates[0][0])
    # except:
    #     birth_date = 0

    # try:
    #     death_date = int(dates[0][1])
    # except:
    #     death_date = 0
    
    # return birth_date, death_date


def duplicates(qualifiers_list):
    duplicates = {}
    for q in qualifiers_list:
        
        duplicates[q] = duplicates.get(q, 0) + 1
    print("-----------------------------", duplicates)    
    return duplicates
        



def get_qualifiers_dict(record, dates_dict, dates, qualifiers='', list_with_qualifiers=[]):
    
    
    """
    teste

    8	decade	+2010-00-00T00:00:00Z	2010s	Any date in range 2010-2019 with precision 8 is interpreted as 2010s.
7	century	+1801-00-00T00:00:00Z	19th century	Any date in range 1801-1900 with precision 7 is interpreted as 19th century. This follows strict historical definition of century as explained in Wikipedia article. This might be counterintuitive to some, especially since it does not overlap with definition of decades. Also in some languages people do not use term like 19th century, but something equivalent to eighteen hundreds (1800s).
    
    
    
    
    # Since there may be more than one qualifier in the birth or death dates
    # create a dictionnary with lists containing the qualifiers before and after the hifen
    qualifiers_list = []
    qualifiers_dict = {}
    hifen_index = 0
    qualifiers_positions = {}
    """
    print("DATES: ", dates)
    # find_qualifier = re.findall(f'({qualifiers})+|(-)', dates)
    # count = 0

    markers_pattern = r'(\bca\b|\bfl\b|\bdps\b|\bpost\b|--|\?|ca\.|fl\.|dps\.|post\.|-)'
    numbers_pattern = '([0-9]+)'
    number_of_hiphens = re.findall('-', dates)
    # 13/09/2024
    dates = dates.replace('[', '').replace(']', '') # remove the square brackets because it interferes with producing the wright qualifiers
    
    # Initialize result lists
    birth_result = []
    death_result = []
    
    # Split the string on the hyphen that separates birth and death dates
    parts = dates.split('-')
    
    # Process birth part
    if len(parts) > 0:
        birth_part = parts[0].strip()
        # birth_part = birth_part.replace('[', '').replace(']', '')
        birth_matches = re.findall(markers_pattern, birth_part)
        for match in birth_matches:
            match = match.strip()
            if match and match not in birth_result:
                birth_result.append(match)
        
        # If birth_part ends with a marker, include it
        if re.search(markers_pattern + r'$', birth_part):
            last_marker = re.search(markers_pattern + r'$', birth_part).group()
            if last_marker not in birth_result:
                birth_result.append(last_marker)
        
    # Process death part
    if len(parts) > 1:
        death_part = parts[1].strip()
        # death_part = death_part.replace('[', '').replace(']', '')
        death_matches = re.findall(markers_pattern, death_part)
        for match in death_matches:
            match = match.strip()
            if match and match not in death_result:
                death_result.append(match)
        
        # If death_part ends with a marker, include it
        if re.search(markers_pattern + r'$', death_part):
            last_marker = re.search(markers_pattern + r'$', death_part).group()
            if last_marker not in death_result:
                death_result.append(last_marker)
    
    # Handle cases where the death part is followed by a '?' (optional death date indicator)
    if dates.endswith('?') and '?' not in death_result:
        death_result.append('?')
    
    # Handle cases where birth part ends with '?'
    if birth_part.endswith('?') and '?' not in birth_result:
        birth_result.append('?')
    
    if '-' in birth_result:
        f.write(f'\nBIRTH RESULT: {birth_result}')
        f.flush()
    # print("DEATH_PART: ", birth_part)
    # Get the dates
    numbers_matches = re.findall(numbers_pattern, dates)
    
    # Get the second date (death date) index, to find out the number of hifens that preceed it
    death_date_index = 0
    try: 
        death_date_index = dates.find(numbers_matches[1])
    except:
        pass    

    # Find the index of the hifens in the birth dates
    
    try:
       birth_one_hifen_index = dates.find('-')
    except:
        pass      
    
    
    try:
       birth_two_hifens_index = dates.find('--')
    except:
        pass   

    try:
        birth_three_hifens_index = dates.find('---')
    except:
        pass


    # Find the index of the hifens in the death dates    

    try:
       death_one_hifen_index = dates.rfind('-')
    except:
        pass  

    try:
       death_two_hifens_index = dates.rfind('--')
    except:
        pass   

    try:
        death_three_hifens_index = dates.rfind('---')
    except:
        pass

        
    
    try:
        numbers_len = len(numbers_matches[0])
    except:
        pass
    # print("death_two_hifens_index", dates[-1])
    # print("#########", re.search('[0-9]+', dates).group())
    # Check if the hifens exist and if it exists append it
    # Append to the birth date qualifiers
    # Used replace because of the separated hifens (ca 18- -)

    # 18---
    if '---' in dates.replace(' ', '') and birth_three_hifens_index < death_date_index:
        birth_result.append('--')
    # Para os casos em que não existe data de morte, e a data de nascimento tem 2 ou 3 hifens
    
    # 18---1815 - confirmar
    elif '---' in dates.replace(' ', '') or '--' in dates.replace(' ', '') and death_date_index == 0:
        birth_result.append('--')
    # elif '--' in dates.replace(' ', '') and '-' not in birth_result and death_date_index == 0:
    #     birth_result.append('--')
    # 192--1980
    elif '--' in dates.replace(' ', '') and birth_two_hifens_index < death_date_index and len(numbers_matches) == 2:
        birth_result.append('-')

    # elif '--' in dates.replace(' ', '') and '-' not in birth_result and birth_two_hifens_index < death_date_index and len(numbers_matches) == 2:
    #     birth_result.append('--')
    elif '-' in dates.replace(' ', '') and birth_one_hifen_index and len(numbers_matches) == 1 and len(re.search('[0-9]+', dates).group()) == 3 and not birth_part.endswith('?'):  # fl. 166-
        birth_result.append('-')
      
    

    
    # Append to the dearth date qualifiers
    if '---' in dates.replace(' ', '') and '-' not in death_result and death_three_hifens_index > death_date_index and len(numbers_matches) == 2:
        death_result.append('---')
    elif '--' in dates.replace(' ', '') and '-' not in death_result and death_two_hifens_index > death_date_index and len(numbers_matches) == 2:
        death_result.append('--')
    elif '-' in dates.replace(' ', '') and '-' not in death_result and death_one_hifen_index > death_date_index and len(numbers_matches) == 2:
        death_result.append('-')    
    elif '-' in dates.replace(' ', '') and dates[-1] == '-' and death_two_hifens_index == -1 and death_three_hifens_index == -1 and len(number_of_hiphens) > 1:
        death_result.append('-')       
    # if birth_part.endswith('--') and '-' not in birth_result:
    #     birth_result.append('?')    
    
    
    # Create final result dictionary
    result = {
        'birth_date': birth_result if birth_result else '',
        'death_date': death_result if death_result else ''
    }

    dates_utf8 = dates.encode('utf-8')
    
    f.write(f"\n\n{record} - {dates_utf8}")
    f.write(f"\nQUALIFIERS: {result}")

    # f.write(f"\n{record} - {dates_dict}")
    
    f.flush()    
    print("QUALIFIERS: ", result)
    return result
    


def get_dates_dict(dates):
    dates_list = []
    dates_dict = {}
    hifen_index = 0
    find_dates = re.findall(f'([0-9]+)|([-])|([0-9]+)', dates)
    # print("find_dates: ", find_dates)
    for i in range(len(find_dates)):
        for v in range(len(find_dates[i])):
            if len(find_dates[i][v]) > 0:

                dates_list.append(find_dates[i][v])
    try:
        hifen_index = dates_list.index('-')
    except:
        # To get the dates (date of birth) that don't have hifens
        hifen_index = 1000
    
    for i in range(len(dates_list)):
        if i < hifen_index:

            dates_dict['birth_date'] = int(dates_list[i])
            # dates_dict['birth_date_index'] = dates.find(dates_list[i])
        
        # print("i: ", i)      
        if i > hifen_index:
            try:
                int(dates_list[i])
                dates_dict['death_date'] = int(dates_list[i])
                # dates_dict['death_date_index'] = dates.find(dates_list[i])
            except:
                pass    
        else:
            dates_dict['death_date'] = 0
            # dates_dict['death_date_index'] = 0
            
        
        
    return dates_dict



def get_qualifiers_positions():
    pass

# qualifiers_result = get_qualifiers_list(dates, 'ca|fl')
# print(qualifiers_result)
# dates_result = get_dates_list(dates)
# print(dates_result)







    """

    duplicated_qualifiers = duplicates(qualifiers_list)
    print("duplicated_qualifiers: ", duplicated_qualifiers)
    
    # retirei de https://pynative.com/python-find-position-of-regex-match-using-span-start-end/
    for match in re.finditer(f'({qualifiers}+)', dates.lower()):
        # count += 1
        
        
        verificar se o elemento surje mais do que 1 vez. ex.. ca 1554-ca 1638
        
        
        
        if match.group() in qualifiers_positions:
            
            qualifiers_positions[match.group()] = match.start()
        else:
        
            qualifiers_positions[match.group()] = match.start()
        
        print("match", match.group(), "start index", match.start(), "End index", match.end())
 
    f.write(f"\n\n\nQUALIFIERS_POSITIONS: {qualifiers_positions}")
    f.flush()    
    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&", qualifiers_positions)
    
    # Get qualifiers indexes
    for q in range(len(find_qualifier)):
        for q2 in range(len(find_qualifier[q])):
            # print("########", find_qualifier[q][q2])
            print("#####################", find_qualifier[q][q2])
            if find_qualifier[q][q2] != '':
                qualifier_position = dates.find(find_qualifier[q][q2])
                qualifiers_positions[find_qualifier[q][q2]] = qualifier_position

    qualifiers_before_hifen = []                
    qualifiers_after_hifen = []
    print("DATAS DATAS: ", dates.lower())
    print("DATES: ", dates)
    
    print("\nQUALIFIERS_POSITIONS: ", qualifiers_positions)
    https://pynative.com/python-find-position-of-regex-match-using-span-start-end/
    
    find_numbers_indexes = "".join(find_qualifier)
    print("FIRST NUMBER INDEX: ", find_numbers_indexes)
    res = re.search(r'\d', find_qualifier)
    first_number = res.span()

    # Extract the numbers
    numbers = re.findall('[0-9]+', dates)
    # print("NUMBERS NUMBERS: ", len(numbers))

    # print("FIRST: ", find_qualifier[0][0])
    birth = []
    death = []
    count = 0
    print("QUALIFIERS_POSITIONS: ", qualifiers_positions)
    for k, v in qualifiers_positions.items():
        # print("###########", find_qualifier[i][0])
        print("VALUE: ", v)
        print("NUMBERS: ", numbers)
        # print("dates_dict['death_date_index']: ", dates_dict['death_date_index'])
        print("V: ", v, " - ", "Index: ", dates_dict['death_date_index'])
        
        
        try:
            list(qualifiers_positions.keys())[-1]
        except:
            continue
        
        
        
       
                                    
        if '?-' in dates and list(qualifiers_positions.keys())[0] == '?' and k == '?' and v < dates_dict['death_date_index']:
            birth.append(k)
            print("K1_1: ", birth)
            qualifiers_dict['qualifiers_birth_date'] = birth
        
        if list(qualifiers_positions.keys())[0] == 'ca' and v < dates_dict['death_date_index']:
            birth.append(k)
            print("K1_1: ", birth)
            qualifiers_dict['qualifiers_birth_date'] = birth        
        
        
        
        
        
        if '-?' in dates and list(qualifiers_positions.keys())[-1] == '?' and k == '?':
            death.append(k)
            print("K2_1: ", death)
            qualifiers_dict['qualifiers_death_date'] = death            
        
        
        
        
        
        
        
        
        
        
        if '?-' in dates and k == '?' and v < dates_dict['death_date_index']:
                    birth.append(k)
                    print("K2_3: ", birth)
                    qualifiers_dict['qualifiers_birth_date'] = birth      



        if '-?' in dates and k == '?' and v > dates_dict['death_date_index']:
                    death.append(k)
                    print("K2_3: ", death)
                    qualifiers_dict['qualifiers_death_date'] = death
        
        
        
        
        
        
        
        

        
        
        # If dates has only one date
        if dates_dict['death_date_index'] == 0:
            # pass

            
                
        
                
            if v < len(dates):
                birth.append(k)
                    # print("K1_1: ", k)
                    # print("dates[-1]: ", dates[-1])
                    # print("list(qualifiers_positions.keys())[-1]: ", list(qualifiers_positions.keys())[-1])
                    # print("birth: ", birth)
            if dates[-1] == "-" and list(qualifiers_positions.keys())[-1] == '-':
                birth.pop()
            if len(birth) > 0:
                qualifiers_dict['qualifiers_birth_date'] = birth
        
        
        # para os que têm duas datas
        elif dates_dict['death_date_index'] > 0:
            
            
            
            # Quando só tem um hifen
            if len(qualifiers_positions) == 1 and v < dates_dict['death_date_index'] and '?-' not in dates:
                birth.append(k)
                print("K2_0: ", birth)
                qualifiers_dict['qualifiers_birth_date'] = birth
            else:
                if v < dates_dict['death_date_index'] and '?-' not in dates:
                    birth.append(k)
                    print("K2_1: ", birth)
                    qualifiers_dict['qualifiers_birth_date'] = birth
                if dates_dict['death_date_index'] > 0:
                    try:
                        birth[-1][-1]
                    except:
                        pass
                    else: # registo 562
                        print("====================", len(birth[-1]))
                        if len(birth[-1]) == 3 and '-' in birth[-1]:
                            to_pop_index = len(birth[-1]) - 1
                        elif len(birth[-1]) == 2 and '-' in birth[-1]:
                            to_pop_index = len(birth[-1]) - 1
                        try:
                            to_pop_index
                        except:
                            pass    
                        else:    
                            if len(birth) > 0 and birth[-1][-1] == "-":
                                birth_copy = birth.copy()
                                del birth[-1]
                                to_append = birth_copy[0][:to_pop_index]
                                if len(to_append) > 0:
                                    birth.append(to_append)    
                                    qualifiers_dict['qualifiers_birth_date'] = birth_copy
                if v > dates_dict['death_date_index']:
                    death.append(k)
                    print("K2_3: ", death)
                    qualifiers_dict['qualifiers_death_date'] = death


                
      
    # try:
    #     qualifiers_dict['qualifiers_birth_date'] 
        
        
    # except:
    #     pass
    # else:
    #     # registo 34 e 263
    #     if dates[dates_dict['death_date_index'] - 1 ] == '-' and len(qualifiers_dict['qualifiers_birth_date'][-1]) == 1:
    #         print("--------------------------------", qualifiers_dict['qualifiers_birth_date'])    
    #         del qualifiers_dict['qualifiers_birth_date'][-1]               
    #     # para estes casos: 1547-1615?
    #     if qualifiers_dict['qualifiers_birth_date'] == []:
    #         del qualifiers_dict['qualifiers_birth_date']
    
    
    f.write(f"\nQUALIFIERS_DICT: {qualifiers_dict}")
    f.flush()






    
    If there is only one hifen, don't put it
    If there is not a birth date, ignore everything after the separator
    If there is not a death date, the data after the separator should used in the birth date
    
    
    if len(qualifiers_list) > 0:
        if qualifiers_list[0] == '-':
            qualifiers_list.remove(qualifiers_list[0])
    f.write(f"\n\nQualifiers: {record} - {qualifiers_list}")
    f.flush()
    
    # Find where the hifen is located inside the list
    # to separate the birth and death dates
    # try:
    #     hifen_index = qualifiers_list.index('-')
    # except: 
    #     # To get any text that exists
    #     hifen_index = 1000
    
    
    # for i in range(len(qualifiers_list)):
        
    #     # If the hifen is the first element of the hifen_index list
    #     # then it hasn't any circa or floruit
    #     if hifen_index > 0:
    #         if i < hifen_index:
    #             qualifiers_before_hifen.append(qualifiers_list[i])
    #             qualifiers_dict['birth_date'] = qualifiers_before_hifen
            
    #         if i > hifen_index:
    #             qualifiers_after_hifen.append(qualifiers_list[i])
    #             qualifiers_dict['death_date'] = qualifiers_after_hifen

    #         if 'birth_date' not in qualifiers_dict:
    #             qualifiers_dict['birth_date'] = []

    #         if 'death_date' not in qualifiers_dict:
    #             qualifiers_dict['death_date'] = []
    
  
    
    return qualifiers_dict
        

       """   
    
