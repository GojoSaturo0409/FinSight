import React from 'react';
import { ArrowUpRight, ArrowDownRight, CreditCard, DollarSign, Target, Bell } from 'lucide-react';
import { AuthProvider, useAuth } from './components/AuthContext';
import LoginPage from './components/LoginPage';
import RegisterPage from './components/RegisterPage';
import TransactionTable from './components/TransactionTable';
import BudgetPanel from './components/BudgetPanel';
import CurrencyConverter from './components/CurrencyConverter';
import Header from './components/Header';
import ExpenseChart from './components/ExpenseChart';
import SpendingTrendsChart from './components/SpendingTrendsChart';
import NetWorthChart from './components/NetWorthChart';
import PortfolioPanel from './components/PortfolioPanel';
import RecommendationsPanel from './components/RecommendationsPanel';
import ReportExport from './components/ReportExport';
import ManualEntryForm from './components/ManualEntryForm';
import CSVUpload from './components/CSVUpload';
import PlaidLinkButton from './components/PlaidLinkButton';
import { CurrencyProvider, useCurrency } from './components/CurrencyContext';
import { apiFetch } from './api';

function Dashboard() {
  const { isAuthenticated } = useAuth();
  const { format } = useCurrency();
  const [transactions, setTransactions] = React.useState<any[]>([]);
  const [investmentValue, setInvestmentValue] = React.useState(0);
  const [budgetAlerts] = React.useState<string[]>([]);
  const [activeTab, setActiveTab] = React.useState('dashboard');
  const [authPage, setAuthPage] = React.useState<'login' | 'register'>('login');
  const [loadingDemo, setLoadingDemo] = React.useState(false);

  const fetchTransactions = React.useCallback(async () => {
    try {
      const data = await apiFetch('/ingestion/transactions');
      setTransactions(data.data || []);
    } catch {
      setTransactions([]);
    }
  }, []);

  const loadDemoData = async () => {
    setLoadingDemo(true);
    try {
      await apiFetch('/ingestion/demo-data', { method: 'POST' });
      await apiFetch('/budget/evaluate-auto', { method: 'POST' });
      fetchTransactions();
    } catch (e) {
      console.error("Failed to load demo data", e);
    } finally {
      setLoadingDemo(false);
    }
  };

  const fetchPortfolio = React.useCallback(async () => {
    try {
      const data = await apiFetch('/investments/portfolio');
      const val = data.portfolio.reduce((sum: number, item: any) => sum + (item.total_value || 0), 0);
      setInvestmentValue(val);
    } catch {
      setInvestmentValue(0);
    }
  }, []);

  React.useEffect(() => {
    fetchTransactions();
    fetchPortfolio();
  }, [fetchTransactions, fetchPortfolio]);

  const totalSpend = transactions.filter(t => t.category !== 'Income').reduce((s, t) => s + t.amount, 0);
  const incomeFromTx = transactions.filter(t => t.category === 'Income').reduce((s, t) => s + t.amount, 0);
  const totalIncome = incomeFromTx > 0 ? incomeFromTx : 0;
  const savingsRatio = totalIncome > 0 ? Math.round(((totalIncome - totalSpend) / totalIncome) * 100) : 0;
  const balance = totalIncome - totalSpend;
  const netWorth = balance + investmentValue;

  if (!isAuthenticated) {
    if (authPage === 'register') {
      return <RegisterPage onSwitchToLogin={() => setAuthPage('login')} />;
    }
    return <LoginPage onSwitchToRegister={() => setAuthPage('register')} />;
  }

  return (
    <div className="min-h-screen bg-neutral-950 text-white font-sans selection:bg-indigo-500/30">
      <Header activeTab={activeTab} onTabChange={setActiveTab} />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

        {activeTab === 'dashboard' && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="bg-neutral-900/50 backdrop-blur-xl border border-white/5 rounded-2xl p-6 flex flex-col justify-between hidden md:flex">
                <div className="flex justify-between items-center text-neutral-400">
                  <span>Total Net Worth</span>
                  <DollarSign size={20} className="text-emerald-400" />
                </div>
                <div className="mt-4">
                  <span className="text-4xl font-bold tracking-tight">{format(netWorth)}</span>
                  <div className={`flex items-center mt-2 text-sm ${balance >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                    <span>Cash: {format(balance)} | Inv: {format(investmentValue)}</span>
                  </div>
                </div>
              </div>

              <div className="bg-neutral-900/50 backdrop-blur-xl border border-white/5 rounded-2xl p-6 flex flex-col justify-between hidden md:flex">
                <div className="flex justify-between items-center text-neutral-400">
                  <span>Monthly Spend</span>
                  <CreditCard size={20} className="text-rose-400" />
                </div>
                <div className="mt-4">
                  <span className="text-4xl font-bold tracking-tight">{format(totalSpend)}</span>
                  <div className="flex items-center mt-2 text-rose-400 text-sm">
                    <span className="bg-rose-500/20 text-rose-300 font-medium px-2 py-0.5 rounded mr-2">Info</span>
                    <span>across {transactions.length} transactions</span>
                  </div>
                </div>
              </div>

              <div className="bg-gradient-to-br from-indigo-500/20 to-purple-500/20 backdrop-blur-xl border border-indigo-500/20 rounded-2xl p-6 relative overflow-hidden group">
                <div className="flex justify-between items-center text-indigo-300">
                  <span>Savings Goal</span>
                  <Target size={20} />
                </div>
                <div className="mt-4 relative z-10">
                  <div className="text-4xl font-bold tracking-tight text-white">{Math.max(0, Math.min(savingsRatio, 100))}%</div>
                  <div className="w-full bg-white/10 rounded-full h-2 mt-4">
                    <div className="bg-indigo-400 h-2 rounded-full transition-all duration-700" style={{ width: `${Math.max(0, Math.min(savingsRatio, 100))}%` }}></div>
                  </div>
                </div>
              </div>
            </div>

            {budgetAlerts.map((alert, idx) => (
              <div key={idx} className="mb-6 w-full p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl flex items-center gap-3 text-rose-300">
                <Bell size={20} />
                <span>{alert}</span>
              </div>
            ))}

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <div className="lg:col-span-2 space-y-8">
                <ExpenseChart transactions={transactions} />
                <TransactionTable transactions={transactions} onRefresh={fetchTransactions} />
              </div>
              <div className="space-y-6">
                <BudgetPanel />
                <CurrencyConverter />
                <div className="bg-neutral-900/50 backdrop-blur-xl border border-white/5 rounded-2xl p-6">
                  <h3 className="text-lg font-bold mb-2">Linked Accounts</h3>
                  <div className="space-y-3">
                    <PlaidLinkButton onSuccess={fetchTransactions} />
                    <button 
                      onClick={loadDemoData} 
                      disabled={loadingDemo}
                      className="w-full py-2.5 bg-neutral-800 hover:bg-neutral-700 rounded-lg text-sm font-medium transition-colors border border-white/10 disabled:opacity-50"
                    >
                      {loadingDemo ? 'Loading...' : 'Load Default Data'}
                    </button>
                  </div>
                </div>
                <ManualEntryForm onTransactionAdded={fetchTransactions} />
                <CSVUpload onUploadComplete={fetchTransactions} />
              </div>
            </div>
          </>
        )}

        {activeTab === 'analytics' && (
          <div className="space-y-8">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <SpendingTrendsChart transactions={transactions} />
              <NetWorthChart transactions={transactions} />
            </div>
            <RecommendationsPanel />
          </div>
        )}

        {activeTab === 'investments' && (
          <div className="max-w-2xl mx-auto">
            <PortfolioPanel />
          </div>
        )}

        {activeTab === 'reports' && (
          <div className="max-w-4xl mx-auto">
            <ReportExport />
          </div>
        )}
      </main>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <CurrencyProvider>
        <Dashboard />
      </CurrencyProvider>
    </AuthProvider>
  );
}

export default App;
