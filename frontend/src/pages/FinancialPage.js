import React from 'react';
import DashboardLayout from '../components/DashboardLayout';
import { Card, CardContent } from '../components/ui/card';
import { DollarSign } from 'lucide-react';

const FinancialPage = () => {
  return (
    <DashboardLayout>
      <div className="min-h-[60vh] flex items-center justify-center" data-testid="financial-page">
        <Card className="border-gray-200 max-w-md w-full">
          <CardContent className="py-16 text-center">
            <div className="w-16 h-16 rounded-full bg-gray-100 flex items-center justify-center mx-auto mb-4">
              <DollarSign size={32} className="text-gray-400" />
            </div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2" style={{ fontFamily: 'Manrope, sans-serif' }}>
              Financeiro
            </h2>
            <p className="text-gray-500">Em desenvolvimento</p>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
};

export default FinancialPage;
