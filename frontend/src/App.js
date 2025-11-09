import React, { useState } from 'react';
import { Mic, ChevronDown, ChevronUp, TrendingUp, Calendar, Wallet, PieChart, BarChart3, Plus } from 'lucide-react';

const VoiceFinanceDashboard = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [expandedSection, setExpandedSection] = useState(null);
  const [newExpense, setNewExpense] = useState({ amount: '', category: 'food' });

  // Sample data - replace with actual data from your backend
  const todayTotal = 1520;
  const weeklyTotal = 8750;
  const monthlyTotal = 28450;

  const weeklySummary = {
    total: 8750,
    dailyAverage: 1250,
    topCategories: [
      { name: 'Food', amount: 3200 },
      { name: 'Transport', amount: 2100 },
      { name: 'Entertainment', amount: 1800 }
    ]
  };

  const monthlySummary = {
    total: 28450,
    categories: [
      { name: 'Food', amount: 10500 },
      { name: 'Transport', amount: 6200 },
      { name: 'Entertainment', amount: 4500 },
      { name: 'Shopping', amount: 3800 },
      { name: 'Utilities', amount: 3450 }
    ]
  };

  const categoryData = [
    { category: 'Food', total: 10500, budget: 10000, percentage: 105 },
    { category: 'Transport', total: 6200, budget: 4000, percentage: 155 },
    { category: 'Entertainment', total: 4500, budget: 3000, percentage: 150 },
    { category: 'Shopping', total: 3800, budget: 5000, percentage: 76 },
    { category: 'Utilities', total: 3450, budget: 5000, percentage: 69 },
    { category: 'Health', total: 2100, budget: 3000, percentage: 70 }
  ];

  const dailySpending = [
    { day: 'Mon', amount: 1200 },
    { day: 'Tue', amount: 980 },
    { day: 'Wed', amount: 1450 },
    { day: 'Thu', amount: 1100 },
    { day: 'Fri', amount: 1620 },
    { day: 'Sat', amount: 890 },
    { day: 'Sun', amount: 1520 }
  ];

  const categorySpending = [
    { category: 'Food', amount: 3200 },
    { category: 'Transport', amount: 2100 },
    { category: 'Entertainment', amount: 1800 },
    { category: 'Shopping', amount: 950 },
    { category: 'Others', amount: 700 }
  ];

  const recentExpenses = [
    { id: 1, date: '2025-11-08', time: '14:30', amount: 250, category: 'Food', description: 'Lunch' },
    { id: 2, date: '2025-11-08', time: '10:15', amount: 80, category: 'Transport', description: 'Cab' },
    { id: 3, date: '2025-11-07', time: '19:45', amount: 450, category: 'Entertainment', description: 'Movie' },
    { id: 4, date: '2025-11-07', time: '12:00', amount: 350, category: 'Food', description: 'Groceries' },
    { id: 5, date: '2025-11-06', time: '16:20', amount: 120, category: 'Transport', description: 'Metro' }
  ];

  const toggleRecording = () => {
    setIsRecording(!isRecording);
  };

  const toggleSection = (section) => {
    setExpandedSection(expandedSection === section ? null : section);
  };

  const handleAddExpense = () => {
    if (newExpense.amount && newExpense.category) {
      alert(`Added ₹${newExpense.amount} to ${newExpense.category}`);
      setNewExpense({ amount: '', category: 'food' });
    }
  };

  const maxDaily = Math.max(...dailySpending.map(d => d.amount));
  const maxCategory = Math.max(...categorySpending.map(c => c.amount));

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-blue-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-blue-900 mb-2">Voice Finance Tracker</h1>
          <p className="text-blue-700">Track your expenses with voice commands or manual entry</p>
        </div>

        {/* Top Section: Microphone and Dropdowns */}
        <div className="grid grid-cols-12 gap-6 mb-8">
          {/* Microphone Section */}
          <div className="col-span-5">
            <div className="bg-white rounded-2xl shadow-lg p-8 h-full flex flex-col items-center justify-center border-2 border-blue-200">
              <button
                onClick={toggleRecording}
                className={`w-32 h-32 rounded-full flex items-center justify-center transition-all duration-300 ${
                  isRecording
                    ? 'bg-red-500 hover:bg-red-600 shadow-xl shadow-red-300 animate-pulse'
                    : 'bg-blue-600 hover:bg-blue-700 shadow-xl shadow-blue-300'
                }`}
              >
                <Mic className="w-16 h-16 text-white" />
              </button>
              <p className="mt-6 text-lg font-semibold text-blue-900">
                {isRecording ? 'Recording...' : 'Click to Speak'}
              </p>
              <p className="text-sm text-blue-600 mt-2">
                Say commands like "Add 500 to food"
              </p>
            </div>
          </div>

          {/* Dropdown Summaries */}
          <div className="col-span-7 space-y-4">
            {/* Daily Total */}
            <div className="bg-white rounded-xl shadow-md border-2 border-blue-200 overflow-hidden">
              <button
                onClick={() => toggleSection('daily')}
                className="w-full px-6 py-4 flex items-center justify-between hover:bg-blue-50 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <Wallet className="w-5 h-5 text-blue-600" />
                  <span className="font-semibold text-blue-900">Today's Total</span>
                  <span className="text-xl font-bold text-blue-700">₹{todayTotal.toLocaleString('en-IN')}</span>
                </div>
                {expandedSection === 'daily' ? (
                  <ChevronUp className="w-5 h-5 text-blue-600" />
                ) : (
                  <ChevronDown className="w-5 h-5 text-blue-600" />
                )}
              </button>
              {expandedSection === 'daily' && (
                <div className="px-6 py-4 bg-blue-50 border-t border-blue-200">
                  <p className="text-blue-800">
                    You have spent ₹{todayTotal.toLocaleString('en-IN')} today across various categories. 
                    Your daily average for this week is ₹{weeklySummary.dailyAverage.toLocaleString('en-IN')}.
                  </p>
                </div>
              )}
            </div>

            {/* Weekly Total */}
            <div className="bg-white rounded-xl shadow-md border-2 border-blue-200 overflow-hidden">
              <button
                onClick={() => toggleSection('weeklyTotal')}
                className="w-full px-6 py-4 flex items-center justify-between hover:bg-blue-50 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <Calendar className="w-5 h-5 text-blue-600" />
                  <span className="font-semibold text-blue-900">Weekly Total</span>
                  <span className="text-xl font-bold text-blue-700">₹{weeklyTotal.toLocaleString('en-IN')}</span>
                </div>
                {expandedSection === 'weeklyTotal' ? (
                  <ChevronUp className="w-5 h-5 text-blue-600" />
                ) : (
                  <ChevronDown className="w-5 h-5 text-blue-600" />
                )}
              </button>
              {expandedSection === 'weeklyTotal' && (
                <div className="px-6 py-4 bg-blue-50 border-t border-blue-200">
                  <p className="text-blue-800">
                    Your total spending for this week is ₹{weeklyTotal.toLocaleString('en-IN')}. 
                    This represents your expenses from Monday through today.
                  </p>
                </div>
              )}
            </div>

            {/* Weekly Summary */}
            <div className="bg-white rounded-xl shadow-md border-2 border-blue-200 overflow-hidden">
              <button
                onClick={() => toggleSection('weeklySummary')}
                className="w-full px-6 py-4 flex items-center justify-between hover:bg-blue-50 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <TrendingUp className="w-5 h-5 text-blue-600" />
                  <span className="font-semibold text-blue-900">Weekly Summary</span>
                </div>
                {expandedSection === 'weeklySummary' ? (
                  <ChevronUp className="w-5 h-5 text-blue-600" />
                ) : (
                  <ChevronDown className="w-5 h-5 text-blue-600" />
                )}
              </button>
              {expandedSection === 'weeklySummary' && (
                <div className="px-6 py-4 bg-blue-50 border-t border-blue-200">
                  <p className="text-blue-800 mb-3">
                    Weekly spending: ₹{weeklySummary.total.toLocaleString('en-IN')} | 
                    Daily average: ₹{weeklySummary.dailyAverage.toLocaleString('en-IN')}
                  </p>
                  <p className="text-blue-800 font-semibold mb-2">Top Categories:</p>
                  <ul className="space-y-1">
                    {weeklySummary.topCategories.map((cat, idx) => (
                      <li key={idx} className="text-blue-700">
                        • {cat.name}: ₹{cat.amount.toLocaleString('en-IN')}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* Monthly Summary */}
            <div className="bg-white rounded-xl shadow-md border-2 border-blue-200 overflow-hidden">
              <button
                onClick={() => toggleSection('monthlySummary')}
                className="w-full px-6 py-4 flex items-center justify-between hover:bg-blue-50 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <BarChart3 className="w-5 h-5 text-blue-600" />
                  <span className="font-semibold text-blue-900">Monthly Summary</span>
                  <span className="text-xl font-bold text-blue-700">₹{monthlyTotal.toLocaleString('en-IN')}</span>
                </div>
                {expandedSection === 'monthlySummary' ? (
                  <ChevronUp className="w-5 h-5 text-blue-600" />
                ) : (
                  <ChevronDown className="w-5 h-5 text-blue-600" />
                )}
              </button>
              {expandedSection === 'monthlySummary' && (
                <div className="px-6 py-4 bg-blue-50 border-t border-blue-200">
                  <p className="text-blue-800 mb-3">
                    November 2025 total: ₹{monthlySummary.total.toLocaleString('en-IN')}
                  </p>
                  <p className="text-blue-800 font-semibold mb-2">Leading Categories:</p>
                  <ul className="space-y-1">
                    {monthlySummary.categories.map((cat, idx) => (
                      <li key={idx} className="text-blue-700">
                        • {cat.name}: ₹{cat.amount.toLocaleString('en-IN')}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-3 gap-6 mb-8">
          {/* Pie Chart - Category Distribution */}
          <div className="bg-white rounded-xl shadow-lg p-6 border-2 border-blue-200">
            <h3 className="text-lg font-bold text-blue-900 mb-4 flex items-center gap-2">
              <PieChart className="w-5 h-5" />
              Category Distribution
            </h3>
            <div className="relative w-48 h-48 mx-auto mb-4">
              <svg viewBox="0 0 100 100" className="transform -rotate-90">
                {(() => {
                  let currentAngle = 0;
                  const colors = ['#1e40af', '#3b82f6', '#60a5fa', '#93c5fd', '#bfdbfe'];
                  const total = categorySpending.reduce((sum, c) => sum + c.amount, 0);
                  
                  return categorySpending.map((cat, idx) => {
                    const percentage = (cat.amount / total) * 100;
                    const angle = (percentage / 100) * 360;
                    const largeArc = angle > 180 ? 1 : 0;
                    
                    const startX = 50 + 40 * Math.cos((currentAngle * Math.PI) / 180);
                    const startY = 50 + 40 * Math.sin((currentAngle * Math.PI) / 180);
                    const endX = 50 + 40 * Math.cos(((currentAngle + angle) * Math.PI) / 180);
                    const endY = 50 + 40 * Math.sin(((currentAngle + angle) * Math.PI) / 180);
                    
                    const path = `M 50 50 L ${startX} ${startY} A 40 40 0 ${largeArc} 1 ${endX} ${endY} Z`;
                    currentAngle += angle;
                    
                    return (
                      <path
                        key={idx}
                        d={path}
                        fill={colors[idx % colors.length]}
                        stroke="white"
                        strokeWidth="0.5"
                      />
                    );
                  });
                })()}
              </svg>
            </div>
            <div className="space-y-2">
              {categorySpending.map((cat, idx) => {
                const colors = ['bg-blue-900', 'bg-blue-700', 'bg-blue-500', 'bg-blue-400', 'bg-blue-300'];
                return (
                  <div key={idx} className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-2">
                      <div className={`w-3 h-3 rounded ${colors[idx % colors.length]}`}></div>
                      <span className="text-blue-800">{cat.category}</span>
                    </div>
                    <span className="font-semibold text-blue-900">₹{cat.amount}</span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Bar Chart - Daily Spending */}
          <div className="bg-white rounded-xl shadow-lg p-6 border-2 border-blue-200">
            <h3 className="text-lg font-bold text-blue-900 mb-4 flex items-center gap-2">
              <BarChart3 className="w-5 h-5" />
              Last 7 Days Spending
            </h3>
            <div className="h-64 flex items-end justify-around gap-1 px-4">
              {dailySpending.map((day, idx) => {
                const height = (day.amount / maxDaily) * 100;
                const isOverBudget = day.amount > 1500;
                return (
                  <div key={idx} className="flex flex-col items-center">
                    <div className="flex flex-col items-center justify-end h-52">
                      <div className="relative group">
                        <div
                          className={`w-10 rounded-t transition-all hover:opacity-80 ${
                            isOverBudget ? 'bg-red-500' : 'bg-blue-600'
                          }`}
                          style={{ height: `${(height / 100) * 208}px` }}
                        ></div>
                        <div className="absolute bottom-full mb-2 left-1/2 transform -translate-x-1/2 bg-blue-900 text-white px-2 py-1 rounded text-xs whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity">
                          ₹{day.amount}
                          {isOverBudget && <div className="text-red-300 text-xs">Over budget!</div>}
                        </div>
                      </div>
                    </div>
                    <span className="text-xs text-blue-700 mt-2 font-medium">{day.day}</span>
                  </div>
                );
              })}
            </div>
            <div className="mt-4 pt-4 border-t border-blue-200">
              <div className="flex items-center gap-3 text-xs">
                <div className="flex items-center gap-1">
                  <div className="w-3 h-3 bg-blue-600 rounded"></div>
                  <span className="text-blue-700">Normal</span>
                </div>
                <div className="flex items-center gap-1">
                  <div className="w-3 h-3 bg-red-500 rounded"></div>
                  <span className="text-blue-700">Over Budget</span>
                </div>
              </div>
            </div>
          </div>

          {/* Bar Chart - Category Spending */}
          <div className="bg-white rounded-xl shadow-lg p-6 border-2 border-blue-200">
            <h3 className="text-lg font-bold text-blue-900 mb-4 flex items-center gap-2">
              <BarChart3 className="w-5 h-5" />
              Category Spending (7 Days)
            </h3>
            <div className="h-64 flex items-end justify-around gap-1 px-4">
              {categorySpending.map((cat, idx) => {
                const height = (cat.amount / maxCategory) * 100;
                const budgetLimits = { Food: 2500, Transport: 1500, Entertainment: 1500, Shopping: 1000, Others: 500 };
                const isOverBudget = cat.amount > (budgetLimits[cat.category] || 1000);
                return (
                  <div key={idx} className="flex flex-col items-center">
                    <div className="flex flex-col items-center justify-end h-52">
                      <div className="relative group">
                        <div
                          className={`w-10 rounded-t transition-all hover:opacity-80 ${
                            isOverBudget ? 'bg-red-500' : 'bg-blue-600'
                          }`}
                          style={{ height: `${(height / 100) * 208}px` }}
                        ></div>
                        <div className="absolute bottom-full mb-2 left-1/2 transform -translate-x-1/2 bg-blue-900 text-white px-2 py-1 rounded text-xs whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity z-10">
                          ₹{cat.amount}
                          {isOverBudget && <div className="text-red-300 text-xs">Alert!</div>}
                        </div>
                      </div>
                    </div>
                    <span className="text-xs text-blue-700 mt-2 font-medium text-center leading-tight">{cat.category}</span>
                  </div>
                );
              })}
            </div>
            <div className="mt-4 pt-4 border-t border-blue-200">
              <div className="flex items-center gap-3 text-xs">
                <div className="flex items-center gap-1">
                  <div className="w-3 h-3 bg-blue-600 rounded"></div>
                  <span className="text-blue-700">Within Budget</span>
                </div>
                <div className="flex items-center gap-1">
                  <div className="w-3 h-3 bg-red-500 rounded"></div>
                  <span className="text-blue-700">Budget Alert</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Expenses */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8 border-2 border-blue-200">
          <h3 className="text-xl font-bold text-blue-900 mb-4">Recent Expenses</h3>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b-2 border-blue-200">
                  <th className="text-left py-3 px-4 text-blue-900 font-semibold">Date</th>
                  <th className="text-left py-3 px-4 text-blue-900 font-semibold">Time</th>
                  <th className="text-left py-3 px-4 text-blue-900 font-semibold">Amount</th>
                  <th className="text-left py-3 px-4 text-blue-900 font-semibold">Category</th>
                  <th className="text-left py-3 px-4 text-blue-900 font-semibold">Description</th>
                </tr>
              </thead>
              <tbody>
                {recentExpenses.map((expense) => (
                  <tr key={expense.id} className="border-b border-blue-100 hover:bg-blue-50 transition-colors">
                    <td className="py-3 px-4 text-blue-800">{expense.date}</td>
                    <td className="py-3 px-4 text-blue-800">{expense.time}</td>
                    <td className="py-3 px-4 text-blue-900 font-semibold">₹{expense.amount}</td>
                    <td className="py-3 px-4">
                      <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                        {expense.category}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-blue-700">{expense.description}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Add Expense Manually */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8 border-2 border-blue-200">
          <h3 className="text-xl font-bold text-blue-900 mb-4 flex items-center gap-2">
            <Plus className="w-6 h-6" />
            Add Expense Manually
          </h3>
          <div className="flex gap-4 items-end">
            <div className="flex-1">
              <label className="block text-sm font-semibold text-blue-900 mb-2">Amount (₹)</label>
              <input
                type="number"
                value={newExpense.amount}
                onChange={(e) => setNewExpense({ ...newExpense, amount: e.target.value })}
                placeholder="Enter amount"
                className="w-full px-4 py-3 border-2 border-blue-200 rounded-lg focus:outline-none focus:border-blue-500 text-blue-900"
              />
            </div>
            <div className="flex-1">
              <label className="block text-sm font-semibold text-blue-900 mb-2">Category</label>
              <select
                value={newExpense.category}
                onChange={(e) => setNewExpense({ ...newExpense, category: e.target.value })}
                className="w-full px-4 py-3 border-2 border-blue-200 rounded-lg focus:outline-none focus:border-blue-500 text-blue-900"
              >
                <option value="food">Food</option>
                <option value="transport">Transport</option>
                <option value="entertainment">Entertainment</option>
                <option value="shopping">Shopping</option>
                <option value="utilities">Utilities</option>
                <option value="health">Health</option>
                <option value="other">Other</option>
              </select>
            </div>
            <button
              onClick={handleAddExpense}
              className="px-8 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors shadow-md"
            >
              Add Expense
            </button>
          </div>
        </div>

        {/* Category Summary */}
        <div className="bg-white rounded-xl shadow-lg p-6 border-2 border-blue-200">
          <h3 className="text-xl font-bold text-blue-900 mb-6">Category Summary</h3>
          <div className="space-y-3">
            {categoryData.map((cat, idx) => (
              <div key={idx} className="border-b border-blue-100 pb-3 last:border-b-0">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-semibold text-blue-900">{cat.category}</span>
                  <div className="flex items-center gap-4">
                    <span className="text-sm text-blue-700">
                      ₹{cat.total.toLocaleString('en-IN')} / ₹{cat.budget.toLocaleString('en-IN')}
                    </span>
                    <span className={`text-sm font-semibold ${cat.percentage > 100 ? 'text-red-600' : cat.percentage > 80 ? 'text-yellow-600' : 'text-green-600'}`}>
                      {cat.percentage}%
                    </span>
                  </div>
                </div>
                <div className="relative h-2 bg-blue-100 rounded-full overflow-hidden">
                  <div
                    className={`absolute left-0 top-0 h-full rounded-full transition-all ${
                      cat.percentage > 100 ? 'bg-red-500' : cat.percentage > 80 ? 'bg-yellow-500' : 'bg-green-500'
                    }`}
                    style={{ width: `${Math.min(cat.percentage, 100)}%` }}
                  ></div>
                  {cat.percentage > 80 && (
                    <div className="absolute right-2 top-0 h-full flex items-center">
                      <span className="text-xs text-white font-bold">
                        {cat.percentage > 100 ? '⚠️ Over Budget' : '⚠️ Warning'}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default VoiceFinanceDashboard;