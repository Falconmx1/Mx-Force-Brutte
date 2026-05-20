#!/usr/bin/env python3
"""
Motor de reglas estilo Hashcat para transformar wordlists
"""
import re
import random

class RuleEngine:
    def __init__(self):
        self.rules = []
    
    def load_rules(self, rules_file):
        """Carga reglas desde archivo"""
        with open(rules_file, 'r') as f:
            self.rules = [line.strip() for line in f if line.strip()]
        print(f"📜 Cargadas {len(self.rules)} reglas")
    
    def apply_rule(self, word, rule):
        """Aplica una regla específica a una palabra"""
        result = word
        i = 0
        while i < len(rule):
            op = rule[i]
            
            # Reglas más comunes de Hashcat
            if op == ':':  # No operation
                pass
            elif op == 'l':  # Lowercase all
                result = result.lower()
            elif op == 'u':  # Uppercase all
                result = result.upper()
            elif op == 'c':  # Capitalize
                result = result.capitalize()
            elif op == 't':  # Toggle case
                result = result.swapcase()
            elif op == 'r':  # Reverse
                result = result[::-1]
            elif op == 'd':  # Duplicate
                result = result * 2
            elif op == 'f':  # Reflect (abc -> abccba)
                result = result + result[::-1]
            elif op == '{':  # Rotate left
                result = result[1:] + result[0]
            elif op == '}':  # Rotate right
                result = result[-1] + result[:-1]
            elif op == '$' and i+1 < len(rule):  # Append char
                result += rule[i+1]
                i += 1
            elif op == '^' and i+1 < len(rule):  # Prepend char
                result = rule[i+1] + result
                i += 1
            elif op.isdigit() and i+2 < len(rule):  # Replace char at position
                pos = int(op)
                new_char = rule[i+1]
                if pos < len(result):
                    result = result[:pos] + new_char + result[pos+1:]
                i += 1
            i += 1
        
        return result
    
    def apply_rules(self, word):
        """Aplica todas las reglas a una palabra"""
        results = [word]
        for rule in self.rules:
            try:
                transformed = self.apply_rule(word, rule)
                if transformed != word:
                    results.append(transformed)
            except:
                pass
        return list(set(results))  # Eliminar duplicados
    
    def generate_wordlist(self, base_wordlist, output_file):
        """Genera nueva wordlist aplicando reglas"""
        print(f"🔄 Generando wordlist con reglas...")
        count = 0
        
        with open(base_wordlist, 'r', encoding='utf-8', errors='ignore') as infile:
            words = [line.strip() for line in infile]
        
        with open(output_file, 'w', encoding='utf-8') as outfile:
            for word in words:
                variations = self.apply_rules(word)
                for var in variations:
                    outfile.write(var + '\n')
                    count += 1
        
        print(f"✅ Generadas {count:,} contraseñas desde {len(words):,} originales")
        return output_file
