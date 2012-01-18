//////////////////// DictLookupHelper.proto ////////////////////
#include "dictobject.h"

typedef struct {
    /* dictionary state */
    PyDictEntry *ma_table;

    /* Entries */
    PyDictEntry *entries[0];
} __pyx_DictLookupHelper;


/* Hash is already calculated since identifiers are interned */
#define __pyx_DictLookupHelper_HASH(key) ((PyStringObject *)(key))->ob_shash
//xxx: py3k unicode strings

static __pyx_DictLookupHelper *__Pyx_DictLookupHelper_New(size_t items);
static CYTHON_INLINE
PyObject *__Pyx_DictLookupHelper_GetItem(__pyx_DictLookupHelper *h,
                                         PyDictObject *dict, PyObject *key,
                                         int index);

//////////////////// DictLookupHelper ////////////////////
static
__pyx_DictLookupHelper *__Pyx_DictLookupHelper_New(size_t items)
{
    size_t size = offsetof(__pyx_DictLookupHelper, entries) +
        sizeof(PyDictEntry *) * items;
    __pyx_DictLookupHelper *h;

    h = PyMem_Malloc(size);
    if (!h)
        return (__pyx_DictLookupHelper *) PyErr_NoMemory();
    memset(h, 0, size);
    return h;
}

static CYTHON_INLINE
int __Pyx_DictLookupHelper_is_valid(__pyx_DictLookupHelper *h,
                                    PyDictObject *dict, PyObject *key,
                                    int index)
{
    PyDictEntry *entry = h->entries[index];

    /* Invalid entry or table changed */
    if (!entry || dict->ma_table != h->ma_table ||
        (dict->ma_table + dict->ma_mask) < entry)
        return 0;

    if (entry->me_key != key)
        return 0;

    return 1;
}

static CYTHON_INLINE
PyObject *__Pyx_DictLookupHelper_GetItem(__pyx_DictLookupHelper *h,
                                         PyDictObject *dict, PyObject *key,
                                         int index)
{
    PyDictEntry *entry;

    if (__Pyx_DictLookupHelper_is_valid(h, dict, key, index))
        return h->entries[index]->me_value;

    entry = dict->ma_lookup(dict, key, __pyx_DictLookupHelper_HASH(key));

    if (!entry)
        return NULL;

    if (entry->me_key != key) {
        PyObject *tmp = entry->me_key;
        Py_INCREF(key);
        entry->me_key = key;
        Py_DECREF(tmp);
    }

    h->entries[index] = entry;
    h->ma_table = dict->ma_table;
    return entry->me_value;
}

/* TODO: implement SetItem method */

//////////////////// ModuleLookupHelper.proto ////////////////////
#define __Pyx_ModuleLookupHelper_USED 1

static __pyx_DictLookupHelper *__pyx_m_helper = 0;
static PyDictObject *__pyx_m_dict = 0;

static int __Pyx_ModuleLookupHelper_Init(size_t items);
static PyObject *__Pyx_Module_GetName(PyObject *key, int index);

//////////////////// ModuleLookupHelper ////////////////////
static
int __Pyx_ModuleLookupHelper_Init(size_t items)
{
    __pyx_m_dict = (PyDictObject *) PyModule_GetDict(__pyx_m);
    if (!__pyx_m_dict)
        return -1;
    __pyx_m_helper = __Pyx_DictLookupHelper_New(items);
    if (!__pyx_m_helper)
        return -1;
    return 0;
}

static
PyObject *__Pyx_Module_GetName(PyObject *key, int index)
{
    PyObject *result = __Pyx_DictLookupHelper_GetItem(__pyx_m_helper,
                                                      __pyx_m_dict, key, index);
    if (!result) {
        PyErr_Clear();
        result = PyObject_GetAttr(__pyx_b, key);
        if (!result)
            PyErr_SetObject(PyExc_NameError, key);
    } else {
        Py_INCREF(result);
    }
    return result;
}
