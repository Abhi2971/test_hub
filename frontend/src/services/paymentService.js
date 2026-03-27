import api from './api';

export const paymentService = {
  async createOrder(amount, purpose, referenceId) {
    try {
      const paiseAmount = Math.round(amount * 100);
      const response = await api.post('/payments/create-order', {
        amount: paiseAmount,
        purpose,
        reference_id: referenceId,
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async verifyPayment(orderId, paymentId, signature) {
    try {
      const response = await api.post('/payments/verify', {
        order_id: orderId,
        payment_id: paymentId,
        signature,
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async getPayments(params = {}) {
    try {
      const response = await api.get('/payments', { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async getPayment(id) {
    try {
      const response = await api.get(`/payments/${id}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async getWallet() {
    try {
      const response = await api.get('/wallet');
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async getTransactions(page = 1) {
    try {
      const response = await api.get('/wallet/transactions', { params: { page } });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async topUp(amountRupees) {
    try {
      const paiseAmount = Math.round(amountRupees * 100);
      const response = await api.post('/wallet/topup', { amount: paiseAmount });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  initiateRazorpay(orderData, onSuccess, onFailure) {
    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = 'https://checkout.razorpay.com/v1/checkout.js';
      script.onload = () => {
        try {
          const rzp = window.Razorpay({
            key: import.meta.env.VITE_RAZORPAY_KEY_ID,
            ...orderData,
            handler: (response) => {
              if (onSuccess) {
                onSuccess(response);
              }
            },
          });
          rzp.on('payment.failed', (response) => {
            if (onFailure) {
              onFailure({
                code: response.error.code,
                description: response.error.description,
                reason: response.error.reason,
                source: response.error.source,
              });
            }
          });
          rzp.open();
          resolve();
        } catch (error) {
          reject(error);
        }
      };
      script.onerror = () => {
        reject(new Error('Failed to load Razorpay checkout script'));
      };
      document.body.appendChild(script);
    });
  },
};

export const subscriptionService = {
  async getStudentPlans(page = 1, limit = 20) {
    try {
      const response = await api.get('/subscriptions/student/plans', { params: { page, limit } });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async getMySubscription() {
    try {
      const response = await api.get('/subscriptions/student/my');
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async subscribeWithWallet(planId) {
    try {
      const response = await api.post('/subscriptions/student/subscribe', {
        plan_id: planId,
        payment_method: 'wallet',
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async subscribeWithRazorpay(planId) {
    try {
      const response = await api.post('/subscriptions/student/subscribe', {
        plan_id: planId,
        payment_method: 'razorpay',
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },
};
