// src/pages/HelpPage.jsx
import React from 'react';
import { 
  Book, 
  MessageCircle, 
  FileText, 
  ExternalLink,
  Search,
  HelpCircle,
  Cpu
} from 'lucide-react';

const HelpCard = ({ icon: Icon, title, description, linkText }) => (
  <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-shadow group cursor-pointer">
    <div className="flex items-center justify-between mb-4">
      <div className="p-3 bg-gray-50 rounded-lg text-blue-600 group-hover:bg-blue-50 transition-colors">
        <Icon size={24} />
      </div>
      <ExternalLink size={16} className="text-gray-300 group-hover:text-blue-500 transition-colors" />
    </div>
    <h3 className="text-lg font-bold text-gray-800 mb-2">{title}</h3>
    <p className="text-sm text-gray-500 mb-4 h-10">{description}</p>
    <span className="text-xs font-bold text-blue-600 uppercase tracking-wide group-hover:underline">
      {linkText || "Read More"} &rarr;
    </span>
  </div>
);

const FaqItem = ({ question, answer }) => (
  <div className="border-b border-gray-100 py-4 last:border-0">
    <h4 className="font-bold text-gray-800 text-sm mb-2 flex items-center gap-2">
      <HelpCircle size={14} className="text-purple-500" />
      {question}
    </h4>
    <p className="text-sm text-gray-600 leading-relaxed ml-6">{answer}</p>
  </div>
);

const HelpPage = () => {
  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      
      {/* Search Header */}
      <div className="text-center space-y-4 py-8">
        <h1 className="text-3xl font-bold text-gray-900">How can we help you?</h1>
        <div className="max-w-xl mx-auto relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
          <input 
            type="text" 
            placeholder="Search documentation, error codes, or tutorials..." 
            className="w-full pl-10 pr-4 py-3 rounded-xl border border-gray-200 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
          />
        </div>
      </div>

      {/* Quick Access Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <HelpCard 
          icon={Book} 
          title="Documentation" 
          description="Comprehensive guides on dashboard features, chart interpretation, and filtering."
          linkText="View Docs"
        />
        <HelpCard 
          icon={Cpu} 
          title="AI Model Logic" 
          description="Learn how our Hybrid Defense engine calculates anomaly scores and threat vectors."
          linkText="Learn More"
        />
        <HelpCard 
          icon={MessageCircle} 
          title="Support Center" 
          description="Contact the SOC engineering team for bug reports or critical incident support."
          linkText="Contact Us"
        />
      </div>

      {/* FAQ Section */}
      <div className="bg-white p-8 rounded-xl border border-gray-200 shadow-sm">
        <div className="flex items-center gap-2 mb-6">
          <FileText className="text-gray-400" />
          <h2 className="text-xl font-bold text-gray-800">Frequently Asked Questions</h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-x-12 gap-y-2">
          <div className="space-y-2">
            <FaqItem 
              question="What is the difference between Signature and AI blocks?" 
              answer="Signature blocks match known attack patterns (e.g., SQLi strings), while AI blocks detect behavioral anomalies in traffic that doesn't match a specific signature."
            />
            <FaqItem 
              question="How do I export event logs for audit?" 
              answer="Navigate to the 'Events Log' page and click the 'Export CSV' button in the top right corner. You can filter by date range before exporting."
            />
          </div>
          <div className="space-y-2">
            <FaqItem 
              question="Why is my traffic being rate-limited?" 
              answer="If the 'Adaptive AI Rate-Limiting' is enabled in Settings, the system may temporarily throttle requests if your IP exceeds the dynamic baseline RPS."
            />
            <FaqItem 
              question="Can I customize the dashboard layout?" 
              answer="Currently, the layout is fixed to standard SOC monitoring views. Custom widgets are planned for the v2.0 release."
            />
          </div>
        </div>
      </div>

      {/* Footer Support Info */}
      <div className="text-center text-sm text-gray-500 pt-8 border-t border-gray-200">
        <p>Still need help? Email the security operations center at <a href="#" className="text-blue-600 font-bold hover:underline">soc-support@example.com</a></p>
      </div>

    </div>
  );
};

export default HelpPage;