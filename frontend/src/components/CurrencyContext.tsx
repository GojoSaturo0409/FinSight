import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { apiFetch } from '../api';

interface CurrencyContextType {
    baseCurrency: string;
    setBaseCurrency: (code: string) => void;
    convert: (amount: number, from?: string) => number;
    format: (amount: number, from?: string) => string;
    rates: Record<string, number>;
}

const CurrencyContext = createContext<CurrencyContextType | null>(null);

export const SUPPORTED_CURRENCIES = [
    { code: 'USD', symbol: '$' },
    { code: 'EUR', symbol: '€' },
    { code: 'GBP', symbol: '£' },
    { code: 'JPY', symbol: '¥' },
    { code: 'INR', symbol: '₹' },
    { code: 'AUD', symbol: 'A$' },
    { code: 'CAD', symbol: 'C$' },
    { code: 'CHF', symbol: 'CHF' },
    { code: 'CNY', symbol: '¥' },
    { code: 'BRL', symbol: 'R$' },
    { code: 'MXN', symbol: '$' },
];

export const getCurrencySymbol = (code: string) => 
    SUPPORTED_CURRENCIES.find(c => c.code === code)?.symbol || '$';

export const CurrencyProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [baseCurrency, setBaseCurrency] = useState('USD');
    const [rates, setRates] = useState<Record<string, number>>({});

    useEffect(() => {
        const fetchRates = async () => {
            try {
                const data = await apiFetch('/currency/rates');
                if (data.rates) {
                    setRates(data.rates);
                }
            } catch (e) {
                console.error("Failed to load global currency rates:", e);
                // Fallback built-in rates
                setRates({
                    EUR: 0.92, GBP: 0.79, JPY: 149.50, INR: 83.12,
                    AUD: 1.53, CAD: 1.36, CHF: 0.88, CNY: 7.24,
                    BRL: 4.97, MXN: 17.15, USD: 1.0,
                });
            }
        };
        fetchRates();
    }, []);

    // Conversion function: converts FROM a currency (default USD) TO baseCurrency
    const convert = useCallback((amount: number, from = 'USD') => {
        if (!rates[baseCurrency] || !rates[from]) return amount;
        
        // Convert 'from' to USD first (if not USD), then USD to 'baseCurrency'
        // Since rates are 'USD to Target':
        // e.g., if from='EUR', amount in USD = amount / rates['EUR']
        // then, target in JPY = (amount in USD) * rates['JPY']
        
        const amountInUSD = from === 'USD' ? amount : amount / rates[from];
        const converted = baseCurrency === 'USD' ? amountInUSD : amountInUSD * rates[baseCurrency];
        
        return converted;
    }, [baseCurrency, rates]);

    const format = useCallback((amount: number, from = 'USD') => {
        const converted = convert(amount, from);
        const symbol = getCurrencySymbol(baseCurrency);
        
        // JPY generally has no decimal places
        const fractionDigits = baseCurrency === 'JPY' ? 0 : 2;
        
        return `${symbol}${converted.toLocaleString(undefined, {
            minimumFractionDigits: fractionDigits,
            maximumFractionDigits: fractionDigits
        })}`;
    }, [baseCurrency, convert]);

    return (
        <CurrencyContext.Provider value={{ baseCurrency, setBaseCurrency, convert, format, rates }}>
            {children}
        </CurrencyContext.Provider>
    );
};

export const useCurrency = () => {
    const context = useContext(CurrencyContext);
    if (!context) {
        throw new Error('useCurrency must be used within a CurrencyProvider');
    }
    return context;
};
