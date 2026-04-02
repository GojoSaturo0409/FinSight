import React, { useState } from 'react';

const BudgetPanel = () => {
    const [foodBudget, setFoodBudget] = useState(500);

    return (
        <div className="bg-neutral-900/50 backdrop-blur-xl border border-white/5 rounded-2xl p-6">
            <div className="flex justify-between items-center mb-6">
                <h3 className="text-xl font-bold">Budget Limits</h3>
                <span className="text-xs bg-indigo-500/20 text-indigo-300 px-2 py-1 rounded-md border border-indigo-500/30">Active</span>
            </div>

            <div className="space-y-6">
                <div>
                    <div className="flex justify-between text-sm mb-2">
                        <span className="font-medium text-neutral-300">Food & Dining</span>
                        <span className="text-neutral-400">Limit: ${foodBudget}</span>
                    </div>
                    <input
                        type="range"
                        min="100"
                        max="1000"
                        value={foodBudget}
                        onChange={(e) => setFoodBudget(Number(e.target.value))}
                        className="w-full h-1 bg-neutral-800 rounded-lg appearance-none cursor-pointer accent-indigo-500"
                    />
                    <div className="flex justify-between text-xs text-neutral-500 mt-2">
                        <span>Spent: $300</span>
                        <span className="text-emerald-400">60% Used</span>
                    </div>
                </div>

                <div>
                    <div className="flex justify-between text-sm mb-2">
                        <span className="font-medium text-neutral-300">Housing</span>
                        <span className="text-neutral-400">Limit: $2000</span>
                    </div>
                    <div className="w-full bg-neutral-800 rounded-full h-1.5 focus:outline-none">
                        <div className="bg-rose-400 h-1.5 rounded-full" style={{ width: '75%' }}></div>
                    </div>
                    <div className="flex justify-between text-xs text-neutral-500 mt-2">
                        <span>Spent: $1500</span>
                        <span className="text-rose-400">75% Used</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default BudgetPanel;
