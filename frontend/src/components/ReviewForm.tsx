// frontend/src/components/ReviewForm.tsx
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Star } from "lucide-react";
import { createReview, ApiReview } from "@/lib/api"; // Impor fungsi dan tipe

interface ReviewFormProps {
  packageId: number; // ID paket yang akan diulas
  onReviewAdded: (newReview: ApiReview) => void; // Callback untuk memberi tahu parent bahwa review baru telah ditambahkan
}

const ReviewForm: React.FC<ReviewFormProps> = ({
  packageId,
  onReviewAdded,
}) => {
  const [reviewerName, setReviewerName] = useState("");
  const [reviewText, setReviewText] = useState("");
  const [rating, setRating] = useState(0);
  const [hoverRating, setHoverRating] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    if (rating < 1 || rating > 5) {
      setError("Rating harus antara 1 dan 5.");
      setIsLoading(false);
      return;
    }

    try {
      const newReviewData = {
        reviewer_name: reviewerName || "Anonim", // Gunakan nama atau default ke "Anonim"
        review_text: reviewText,
        rating: rating,
        package_id: packageId, // Kirim ID paket
      };

      const newReview = await createReview(newReviewData);
      onReviewAdded(newReview); // Beri tahu parent bahwa review baru telah ditambahkan
      // Reset form
      setReviewerName("");
      setReviewText("");
      setRating(0);
    } catch (err) {
      console.error("Error submitting review:", err);
      setError(err instanceof Error ? err.message : "Gagal mengirim ulasan.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="mt-8 p-6 bg-muted/20 rounded-lg">
      <h3 className="text-xl font-semibold mb-4">Tambahkan Ulasan Anda</h3>
      {error && <p className="text-destructive mb-4">{error}</p>}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <Label htmlFor="reviewerName">Nama (Opsional)</Label>
          <Input
            id="reviewerName"
            value={reviewerName}
            onChange={(e) => setReviewerName(e.target.value)}
            placeholder="Nama Anda"
          />
        </div>
        <div>
          <Label htmlFor="reviewText">Ulasan</Label>
          <Textarea
            id="reviewText"
            value={reviewText}
            onChange={(e) => setReviewText(e.target.value)}
            placeholder="Tulis ulasan Anda tentang paket ini..."
            rows={4}
            required
          />
        </div>
        <div>
          <Label>Rating</Label>
          <div className="flex">
            {[1, 2, 3, 4, 5].map((star) => (
              <button
                key={star}
                type="button"
                className={`p-1 focus:outline-none ${
                  star <= (hoverRating || rating)
                    ? "text-yellow-400"
                    : "text-gray-300"
                }`}
                onClick={() => setRating(star)}
                onMouseEnter={() => setHoverRating(star)}
                onMouseLeave={() => setHoverRating(0)}
              >
                <Star className="w-6 h-6 fill-current" />
              </button>
            ))}
          </div>
        </div>
        <Button type="submit" disabled={isLoading} className="w-full">
          {isLoading ? "Mengirim..." : "Kirim Ulasan"}
        </Button>
      </form>
    </div>
  );
};

export default ReviewForm;
