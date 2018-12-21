#ifndef SYMBOLS_H
#define SYMBOLS_H
#include <vector>
#include <string>
#include <map>

typedef std::vector<std::string> vec_str_t;
typedef std::map<std::string, unsigned int> dict_uint_t;
class Symbols
{
public:
    Symbols(const vec_str_t &symbs, const vec_str_t &unique_symbs);
    ~Symbols();

    /** Return the symbol ID of the atom at site indx */
    unsigned int id(unsigned int indx) const {return symb_ids[indx];};

    /** Check if the symb_id and symbols are consistent */
    bool is_consistent() const;

    /** Set a new symbol */
    void set_symbol(unsigned int indx, const std::string &symb);

    /** Get the array of symbols */
    const vec_str_t& get_symbols() const {return symbols;};

    /** Return the size of the symbol container */
    unsigned int size() const {return symbols.size();};
private:
    unsigned int *symb_ids{nullptr};
    vec_str_t symbols;
    dict_uint_t symb_id_translation;
};
#endif