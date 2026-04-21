import React from 'react';
import { ArrowUpRight, ArrowDownRight, CreditCard, DollarSign, Target, Bell } from 'lucide-react';
import TransactionTable from './components/TransactionTable';
import BudgetPanel from './components/BudgetPanel';
import Header from './components/Header';
import ExpenseChart from './components/ExpenseChart';
import SpendingTrendsChart from './components/SpendingTrendsChart';
import NetWorthChart from './components/NetWorthChart';
import PortfolioPanel from './components/PortfolioPanel';
import RecommendationsPanel from './components/RecommendationsPanel';
import ReportExport from './components/ReportExport';

function App() {
  const [transactions, setTransactions] = React.useState<any[]>([]);
  const [budgetAlerts] = React.useState(["You are nearing your Food budget limit."]);
  const [activeTab, setActiveTab] = React.useState('dashboard');

  // Mock fetching transactions
  React.useEffect(() => {
    const fetchTxs = async () => {
      // In real scenario, fetches from backend
      setTransactions([
        { id: "1", amount: 120.50, currency: "USD", category: "Food", merchant: "Whole Foods", date: "2024-03-12" },
        { id: "2", amount: 80.00, currency: "USD", category: "Transport", merchant: "Uber", date: "2024-03-14" },
        { id: "3", amount: 1500.00, currency: "USD", category: "Housing", merchant: "Avalon Rent", date: "2024-03-01" },
        { id: "4", amount: 15.99, currency: "USD", category: "Subscriptions", merchant: "Netflix", date: "2024-03-05" },
      ]);
    };
    fetchTxs();
  }, []);

  return (
    <div className="min-h-screen bg-neutral-950 text-white font-sans selection:bg-indigo-500/30">
      <Header activeTab={activeTab} onTabChange={setActiveTab} />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

        {/* ===== DASHBOARD TAB ===== */}
        {activeTab === 'dashboard' && (
          <>
            {/* Top Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="bg-neutral-900/50 backdrop-blur-xl border border-white/5 rounded-2xl p-6 flex flex-col justify-between">
                <div className="flex justify-between items-center text-neutral-400">
                  <span>Total Balance</span>
                  <DollarSign size={20} className="text-emerald-400" />
                </div>
                <div className="mt-4">
                  <span className="text-4xl font-bold tracking-tight">$12,450.00</span>
                  <div className="flex items-center mt-2 text-emerald-400 text-sm">
                    <ArrowUpRight size={16} className="mr-1" />
                    <span>+2.4% from last month</span>
                  </div>
                </div>
              </div>

              <div className="bg-neutral-900/50 backdrop-blur-xl border border-white/5 rounded-2xl p-6 flex flex-col justify-between">
                <div className="flex justify-between items-center text-neutral-400">
                  <span>Monthly Spend</span>
                  <CreditCard size={20} className="text-rose-400" />
                </div>
                <div className="mt-4">
                  <span className="text-4xl font-bold tracking-tight">$1,716.49</span>
                  <div className="flex items-center mt-2 text-rose-400 text-sm">
                    <ArrowDownRight size={16} className="mr-1" />
                    <span>-4.1% from last month</span>
                  </div>
                </div>
              </div>

              <div className="bg-gradient-to-br from-indigo-500/20 to-purple-500/20 backdrop-blur-xl border border-indigo-500/20 rounded-2xl p-6 relative overflow-hidden group">
                <div className="flex justify-between items-center text-indigo-300">
                  <span>Savings Goal</span>
                  <Target size={20} />
                </div>
                <div className="mt-4 relative z-10">
                  <div className="text-4xl font-bold tracking-tight text-white">85%</div>
                  <div className="w-full bg-white/10 rounded-full h-2 mt-4">
                    <div className="bg-indigo-400 h-2 rounded-full" style={{ width: '85%' }}></div>
                  </div>
                </div>
              </div>
            </div>

            {/* Alerts block (Mocking Firebase in-app notification Toast) */}
            {budgetAlerts.map((alert, idx) => (
              <div key={idx} className="mb-6 w-full p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl flex items-center gap-3 text-rose-300">
                <Bell size={20} />
                <span>{alert}</span>
              </div>
            ))}

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <div className="lg:col-span-2 space-y-8">
                <ExpenseChart />
                <TransactionTable transactions={transactions} />
              </div>
              <div className="space-y-8">
                <BudgetPanel />

                {/* Sync Button Mock */}
                <div className="bg-neutral-900/50 border border-white/5 rounded-2xl p-6">
                  <h3 className="text-xl font-bold mb-4">Connect Accounts</h3>
                  <p className="text-sm text-neutral-400 mb-6">Link your bank securely using Plaid OAuth.</p>
                  <button className="w-full bg-white text-black font-semibold rounded-xl py-3 hover:bg-neutral-200 transition-colors">
                    Connect via Plaid
                  </button>
                </div>
              </div>
            </div>
          </>
        )}

        {/* ===== ANALYTICS TAB ===== */}
        {activeTab === 'analytics' && (
          <div className="space-y-8">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <SpendingTrendsChart />
              <NetWorthChart />
            </div>
            <RecommendationsPanel />
          </div>
        )}

        {/* ===== INVESTMENTS TAB ===== */}
        {activeTab === 'investments' && (
          <div className="max-w-2xl mx-auto">
            <PortfolioPanel />
          </div>
        )}

        {/* ===== REPORTS TAB ===== */}
        {activeTab === 'reports' && (
          <div className="max-w-2xl mx-auto">
            <ReportExport />
          </div>
        )}

      </main>
    </div>
  );
}

export default App;
