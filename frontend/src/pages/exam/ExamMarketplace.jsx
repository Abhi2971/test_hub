import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { examService } from '../../services/examService';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';
import Badge from '../../components/ui/Badge';

export default function ExamMarketplace() {
  const navigate = useNavigate();
  const [exams, setExams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState({ category: '', price: '' });

  useEffect(() => {
    const fetchExams = async () => {
      setLoading(true);
      try {
        const response = await examService.getMarketplace(filter);
        setExams(response?.data?.items || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchExams();
  }, [filter]);

  const handlePurchase = (examId) => {
    console.log('Purchase exam:', examId);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Exam Marketplace</h1>
      </div>

      <div className="flex gap-4">
        <select
          onChange={(e) => setFilter({ ...filter, category: e.target.value })}
          className="px-4 py-2 border border-gray-300 rounded-lg text-sm"
          value={filter.category}
        >
          <option value="">All Categories</option>
          <option value="math">Mathematics</option>
          <option value="science">Science</option>
          <option value="language">Language</option>
          <option value="technology">Technology</option>
        </select>
        <select
          onChange={(e) => setFilter({ ...filter, price: e.target.value })}
          className="px-4 py-2 border border-gray-300 rounded-lg text-sm"
          value={filter.price}
        >
          <option value="">All Prices</option>
          <option value="free">Free</option>
          <option value="paid">Paid</option>
        </select>
      </div>

      {loading ? (
        <div className="text-center py-12 text-gray-500">Loading exams...</div>
      ) : exams.length === 0 ? (
        <div className="text-center py-12 text-gray-500">No exams available in marketplace</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {exams.map((exam) => (
            <Card key={exam.id}>
              <div className="space-y-3">
                <h3 className="font-semibold text-gray-900">{exam.title}</h3>
                <p className="text-sm text-gray-500 line-clamp-2">{exam.description}</p>
                <div className="flex items-center justify-between">
                  <div className="flex gap-2">
                    <Badge variant="info">{exam.category || 'General'}</Badge>
                  </div>
                  <span className="font-bold text-gray-900">
                    {exam.price === 0 ? 'Free' : `₹${exam.price}`}
                  </span>
                </div>
                <div className="flex items-center justify-between text-sm text-gray-500">
                  <span>{exam.question_count || 0} questions</span>
                  <span>{exam.duration_minutes} min</span>
                </div>
                <Button onClick={() => handlePurchase(exam.id)} className="w-full">
                  Purchase
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
