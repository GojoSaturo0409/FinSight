import React from 'react';

const Header = () => (
    <header className="border-b border-white/5 bg-neutral-950/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
            <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-indigo-500 rounded-xl flex items-center justify-center">
                    <span className="font-bold text-xl text-white">F</span>
                </div>
                <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-white/60">
                    FinSight
                </h1>
            </div>
            <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-neutral-400">
                <a href="#" className="text-white">Dashboard</a>
                <a href="#" className="hover:text-white transition-colors">Transactions</a>
                <a href="#" className="hover:text-white transition-colors">Budgets</a>
                <a href="#" className="hover:text-white transition-colors">Insights</a>
            </nav>
            <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-500 border-2 border-neutral-950 shadow-inner"></div>
        </div>
    </header>
);

export default Header;
