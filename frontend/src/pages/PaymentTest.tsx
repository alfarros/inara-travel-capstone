// D:\inara-travel-capstone\src\pages\PaymentTest.tsx - VERSI PERBAIKAN JSON

import React, { useState } from 'react';
import { Button } from '@/components/ui/button'; // Asumsi Anda punya komponen Button

// --- TIPE DATA DIPERBARUI (SESUAI JSON ANDA) ---
type MidtransRequest = {
  order_id: string;
  gross_amount: number;
  items: Array<{ // Diubah dari 'item_details'
    id: string;
    price: number;
    quantity: number;
    name: string;
  }>;
  customer: { // Diubah dari 'customer_details'
    first_name: string;
    last_name: string;
    email: string;
    phone: string;
  };
};

// Tipe data respons dari backend Anda
type MidtransResponse = {
  token: string;
  redirect_url: string;
};

// Tipe data untuk error 422 dari FastAPI
type FastAPIValidationError = {
  detail: Array<{
    loc: (string | number)[];
    msg: string;
    type: string;
  }>;
};

const PaymentTestPage = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const paket = {
    id: '1',
    name: 'Paket Silver',
    price: 24000000,
  };

  const handlePayment = async () => {
    setIsLoading(true);
    setError(null);

    const orderId = `INARA-TEST-${Date.now()}`;

    // --- OBJEK JSON DIPERBARUI (SESUAI STRUKTUR ANDA) ---
    const paymentData: MidtransRequest = {
      order_id: orderId,
      gross_amount: paket.price,
      items: [
        {
          id: paket.id,
          price: paket.price,
          quantity: 1,
          name: paket.name,
        },
      ],
      customer: {
        first_name: 'Budi',
        last_name: 'Tester',
        email: 'budi.tester@example.com',
        phone: '081234567890',
      },
    };
    // --- AKHIR PERBAIKAN JSON ---

    try {
      // Panggil backend payments-api (Port 8010)
      const response = await fetch('http://localhost:8010/create-transaction', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(paymentData),
      });

      if (!response.ok) {
        let errorMessage = `HTTP error! status: ${response.status}`;
        try {
          const errorData: FastAPIValidationError = await response.json();
          if (response.status === 422 && errorData.detail) {
            const validationErrors = errorData.detail.map((err) => 
              `Field '${err.loc[err.loc.length - 1]}' ${err.msg}`
            ).join(', ');
            errorMessage = `Data tidak valid: ${validationErrors}`;
          }
        } catch (e) {
          // Biarkan pesan error HTTP default
        }
        throw new Error(errorMessage);
      }

      const data: MidtransResponse = await response.json();

      if (data.redirect_url) {
        window.location.href = data.redirect_url;
      } else {
        setError('Respons tidak valid dari server (tidak ada redirect_url).');
      }
    } catch (err: any) {
      console.error('Error saat proses pembayaran:', err);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-lg max-w-sm w-full">
        <h1 className="text-2xl font-bold text-center mb-4">
          Test Halaman Pembayaran
        </h1>
        <div className="border rounded-md p-4 mb-6">
          <h2 className="text-xl font-semibold">{paket.name}</h2>
          <p className="text-lg text-gray-700">
            {new Intl.NumberFormat('id-ID', {
              style: 'currency',
              currency: 'IDR',
              minimumFractionDigits: 0,
            }).format(paket.price)}
          </p>
        </div>

        <Button
          onClick={handlePayment}
          disabled={isLoading}
          className="w-full text-lg"
        >
          {isLoading ? 'Memproses...' : 'Bayar Sekarang (via Midtrans)'}
        </Button>

        {error && (
          <p className="text-red-500 text-sm text-center mt-4">{error}</p>
        )}
      </div>
    </div>
  );
};

export default PaymentTestPage;