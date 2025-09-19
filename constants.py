SIMPLE_NUMBER_TYPES = ['byte', 'ubyte', 'word', 'uword', 'dword', 'udword', 'float']
FACTOR_NUMBER_TYPES = ['byte_factor', 'ubyte_factor', 'word_factor', 'uword_factor', 'dword_factor', 'udword_factor', 'float_factor']
FIXED_NUMBER_TYPES = ['byte_fixed', 'ubyte_fixed', 'word_fixed', 'uword_fixed', 'dword_fixed', 'udword_fixed', 'float_fixed']
SIMPLE_COMPOSITE_TYPES=['string']
FACTOR_COMPOSITE_TYPES=[]
FIXED_COMPOSITE_TYPES=['string_fixed']
NUMBER_TYPES = SIMPLE_NUMBER_TYPES + FACTOR_NUMBER_TYPES + FIXED_NUMBER_TYPES
COMPOSITE_TYPES = SIMPLE_COMPOSITE_TYPES + FACTOR_COMPOSITE_TYPES + FIXED_COMPOSITE_TYPES
DATA_TYPES= {
    'boolean': {
        'data_type': 'boolean',
        'c_type': 'bool',
        'category': 'simple',
        'media': 'boolean',
        'min': 0,
        'max': 1
    },
    'string': {
        'data_type': 'string',
        'c_type': 'char',
        'category': 'simple',
        'media': 'string',
        'min': None,
        'max': None
    },
    'string_fixed': {
        'data_type': 'string_fixed',
        'c_type': 'char',
        'category': 'fixed',
        'media': 'string',
        'min': None,
        'max': None
    },
    'float': {
        'data_type': 'float',
        'c_type': 'float',
        'category': 'simple',
        'media': 'number',
        'min': -1.0,
        'max':  1.0
    },
    'byte': {
        'data_type': 'byte',
        'c_type': 'int8_t',
        'category': 'simple',
        'media': 'number',
        'min': -128,
        'max':  127
    },
    'ubyte': {
        'data_type': 'ubyte',
        'c_type': 'uint8_t',
        'category': 'simple',
        'media': 'number',
        'min': 0,
        'max': 255
    },
    'word': {
        'data_type': 'word',
        'media': 'int16_t',
        'category': 'simple',
        'media': 'number',
        'min': -32768,
        'max':  32767
    },
    'uword': {
        'data_type': 'uword',
        'c_type': 'uint16_t',
        'category': 'simple',
        'media': 'number',
        'min': 0,
        'max': 65535,
    },
    'dword': {
        'data_type': 'dword',
        'c_type': 'int32_t',
        'category': 'simple',
        'media': 'number',
        'min': -2147483648,
        'max':  2147483647
    },
    'udword': {
        'data_type': 'udword',
        'c_type': 'uint32_t',
        'category': 'simple',
        'media': 'number',
        'min': 0,
        'max': 4294967295
    },
    'float_factor': {
        'data_type': 'float',
        'c_type': 'float',
        'category': 'fixed',
        'media': 'number',
        'min': -2147483648,
        'max':  2147483647
    },
    'byte_factor': {
        'data_type': 'byte_factor',
        'c_type': 'int8_t',
        'category': 'factor',
        'media': 'number',
        'min': -128,
        'max':  127
    },
    'ubyte_factor': {
        'data_type': 'ubyte_factor',
        'c_type': 'uint8_t',
        'category': 'factor',
        'media': 'number',
        'min': 0,
        'max': 255
    },
    'word_factor': {
        'data_type': 'word_factor',
        'c_type': 'int16_t',
        'category': 'factor',
        'media': 'number',
        'min': -32768,
        'max':  32768
    },
    'uword_factor': {
        'data_type': 'uword_factor',
        'c_type': 'uint16_t',
        'category': 'factor',
        'media': 'number',
        'min': 0,
        'max': 65535
    },
    'dword_factor': {
        'data_type': 'dword_factor',
        'c_type': 'int32_t',
        'category': 'factor',
        'media': 'number',
        'min': -2147483648,
        'max':  2147483647
    },
    'udword_factor': {
        'data_type': 'udword_factor',
        'c_type': 'uint32_t',
        'category': 'factor',
        'media': 'number',
        'min': -2147483648,
        'max':  2147483647
    },
    'byte_fixed': {
        'data_type': 'byte_fixed',
        'c_type': 'int8_t',
        'category': 'fixed',
        'media': 'number',
        'min': -128,
        'max': 127
    },
    'ubyte_fixed': {
        'data_type': 'ubyte_fixed',
        'c_type': 'uint8_t',
        'category': 'fixed',
        'media': 'number',
        'min': 0,
        'max': 255
    },
    'word_fixed': {
        'data_type': 'word_fixed',
        'c_type': 'int16_t',
        'category': 'fixed',
        'media': 'number',
        'min': -32768,
        'max':  32767
    },
    'uword_fixed': {
        'data_type': 'uword_fixed',
        'c_type': 'uint16_t',
        'category': 'fixed',
        'media': 'number',
        'min': 0,
        'max': 65535
    },
    'dword_fixed': {
        'data_type': 'dword_fixed',
        'c_type': 'int32_t',
        'category': 'fixed',
        'media': 'number',
        'min': -2147483648,
        'max':  2147483647
    },
    'udword_fixed': {
        'data_type': 'udword_fixed',
        'c_type': 'uint32_t',
        'category': 'fixed',
        'media': 'number',
        'min': -2147483648,
        'max':  2147483647
    },
    'float_fixed': {
        'data_type': 'float_fixed',
        'c_type': 'float',
        'category': 'fixed',
        'media': 'number',
        'min': -2147483648,
        'max':  2147483647
    },
    'callback': {
        'data_type': 'callback',
        'c_type': 'void',
        'category': 'callback',
        'media': 'void',
        'min': None,
        'max':  None
    }
}    
