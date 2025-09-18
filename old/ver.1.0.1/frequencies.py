# Печать целочисленных частот и делителей в формате C-массива

def main():
    print(
        '\n\ntypedef struct {\n'
        '   int divider;\n'
        '   int frequency;\n'
        '} frequency_t;\n'
        '\n'
        '\n'
        'static frequency_t s_frequencies[] = {'
        )
    for divider in range(10000, 4, -1):
        freq = 10_000_000 / divider
        # if prev - res > 100:
        if freq.is_integer():
            #print(f'{round(res)} {divider}')
            comment = ''
            if freq >= 100000:
                comment = f'{round(freq)/1000000} MHz'
            elif freq >= 1000:
                comment = f'{round(freq)/1000} kHz'
            else:
                comment = f'{round(freq)} Hz'

            print(f'\t{{{divider}, {round(freq)}}}, // {comment}')
    print('};\n\n')


if __name__ == '__main__':
    main()
