import math
from datetime import datetime
from collections import Counter
from typing import List, Dict, Any, Optional

class StatsService:
    """
    Statistics & Analytics Engine:
    Computes summary metrics, resolution time statistics (mean, median, mode,
    variance, std dev, quartiles, IQR, outliers), and plain-English insights.
    """

    def __init__(self, complaints: List[Dict[str, Any]]):
        self.complaints = complaints

    def get_category_distribution(self) -> Dict[str, int]:
        counts = Counter(c.get("category") or "Unclassified" for c in self.complaints)
        return dict(counts)

    def get_priority_distribution(self) -> Dict[str, int]:
        counts = Counter(c.get("priority") or "Unspecified" for c in self.complaints)
        return dict(counts)

    def get_status_distribution(self) -> Dict[str, int]:
        counts = Counter(c.get("status") or "Open" for c in self.complaints)
        return dict(counts)

    def _calculate_resolution_times_hours(self) -> List[float]:
        """Calculates resolution duration in hours for all resolved complaints."""
        durations = []
        for c in self.complaints:
            if c.get("status") == "Resolved" and c.get("resolved_at") and c.get("created_at"):
                try:
                    # Parse ISO timestamps
                    created = datetime.fromisoformat(c["created_at"].replace("Z", "+00:00"))
                    resolved = datetime.fromisoformat(c["resolved_at"].replace("Z", "+00:00"))
                    diff_hours = (resolved - created).total_seconds() / 3600.0
                    if diff_hours >= 0:
                        durations.append(round(diff_hours, 2))
                except Exception:
                    continue
        return durations

    def get_resolution_stats(self) -> Dict[str, Any]:
        """
        Computes comprehensive statistics on resolution times:
        Mean, median, mode, min, max, range, variance, std dev, Q1, Q3, IQR, outliers.
        """
        durations = self._calculate_resolution_times_hours()

        if not durations:
            return {
                "total_resolved": 0,
                "mean_hours": 0.0,
                "median_hours": 0.0,
                "mode_hours": 0.0,
                "min_hours": 0.0,
                "max_hours": 0.0,
                "range_hours": 0.0,
                "variance_hours": 0.0,
                "std_dev_hours": 0.0,
                "q1_hours": 0.0,
                "q3_hours": 0.0,
                "iqr_hours": 0.0,
                "outlier_threshold_hours": 0.0,
                "outliers_count": 0,
                "interpretation": "No resolved complaints available yet to compute resolution time statistics."
            }

        sorted_dur = sorted(durations)
        n = len(sorted_dur)

        # Mean
        mean_val = sum(sorted_dur) / n

        # Median
        if n % 2 == 1:
            median_val = sorted_dur[n // 2]
        else:
            median_val = (sorted_dur[n // 2 - 1] + sorted_dur[n // 2]) / 2.0

        # Mode
        mode_counts = Counter(sorted_dur)
        mode_val = mode_counts.most_common(1)[0][0]

        # Min, Max, Range
        min_val = sorted_dur[0]
        max_val = sorted_dur[-1]
        range_val = max_val - min_val

        # Variance & Standard Deviation
        if n > 1:
            variance_val = sum((x - mean_val) ** 2 for x in sorted_dur) / (n - 1)
        else:
            variance_val = 0.0
        std_dev_val = math.sqrt(variance_val)

        # Quartiles & IQR
        def get_percentile(arr: List[float], p: float) -> float:
            k = (len(arr) - 1) * p
            f = math.floor(k)
            c = math.ceil(k)
            if f == c:
                return arr[int(k)]
            return arr[int(f)] * (c - k) + arr[int(c)] * (k - f)

        q1_val = get_percentile(sorted_dur, 0.25)
        q3_val = get_percentile(sorted_dur, 0.75)
        iqr_val = q3_val - q1_val
        upper_fence = q3_val + (1.5 * iqr_val)

        outliers = [x for x in sorted_dur if x > upper_fence]

        # Generate plain-English interpretation
        interpretation = self._generate_interpretation(
            mean_val, median_val, std_dev_val, iqr_val, upper_fence, len(outliers), n
        )

        return {
            "total_resolved": n,
            "mean_hours": round(mean_val, 2),
            "median_hours": round(median_val, 2),
            "mode_hours": round(mode_val, 2),
            "min_hours": round(min_val, 2),
            "max_hours": round(max_val, 2),
            "range_hours": round(range_val, 2),
            "variance_hours": round(variance_val, 2),
            "std_dev_hours": round(std_dev_val, 2),
            "q1_hours": round(q1_val, 2),
            "q3_hours": round(q3_val, 2),
            "iqr_hours": round(iqr_val, 2),
            "outlier_threshold_hours": round(upper_fence, 2),
            "outliers_count": len(outliers),
            "interpretation": interpretation
        }

    def _generate_interpretation(
        self, mean_h: float, median_h: float, std_h: float, iqr_h: float, fence_h: float, outliers_cnt: int, total_res: int
    ) -> str:
        """Generates plain-English narrative summarizing statistical insights."""
        lines = []
        lines.append(f"Based on {total_res} resolved complaints, the average resolution time is {mean_h:.1f} hours, with a median of {median_h:.1f} hours.")
        
        if std_h > (mean_h * 0.5):
            lines.append(f"High variance (std dev: {std_h:.1f}h) indicates significant inconsistency in resolution speeds across departments.")
        else:
            lines.append(f"Resolution performance remains relatively consistent across municipal teams (std dev: {std_h:.1f}h).")

        if outliers_cnt > 0:
            lines.append(f"{outliers_cnt} complaint(s) exceeded the outlier threshold of {fence_h:.1f} hours and require administrative attention.")
        else:
            lines.append("No statistical outlier delays were detected in resolution times.")

        return " ".join(lines)

    def get_trends(self) -> Dict[str, Any]:
        """Groups complaints by created date to show submission volume trends."""
        daily_counts = Counter()
        for c in self.complaints:
            date_str = c.get("date") or c.get("created_at") or ""
            if date_str:
                day = date_str[:10]
                daily_counts[day] += 1

        sorted_days = sorted(daily_counts.items())
        return {
            "daily_trends": [{"date": day, "count": count} for day, count in sorted_days]
        }
