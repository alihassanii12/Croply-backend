from django.db.models import Count
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsFarmer
from crops.models import Crop
from farms.models import Farm
from marketplace.models import Listing
from scans.models import Scan
from scans.serializers import ScanSerializer


class AnalyticsSummaryView(APIView):
    """Aggregated statistics scoped to the current farmer's data."""
    permission_classes = [IsAuthenticated, IsFarmer]

    def get(self, request):
        user = request.user
        scans = Scan.objects.filter(user=user).select_related('disease')

        total_scans = scans.count()
        healthy_scans = scans.filter(
            predicted_class__icontains='healthy'
        ).count()
        diseased_scans = (
            scans.exclude(predicted_class='').count() - healthy_scans
        )

        disease_distribution = list(
            scans.exclude(predicted_class='')
            .values('predicted_class')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )
        disease_distribution = [
            {'name': item['predicted_class'], 'count': item['count']}
            for item in disease_distribution
        ]

        recent_scans = ScanSerializer(
            scans[:5], many=True, context={'request': request}
        ).data

        return Response({
            'total_scans': total_scans,
            'healthy_scans': healthy_scans,
            'diseased_scans': diseased_scans,
            'total_farms': Farm.objects.filter(owner=user).count(),
            'total_crops': Crop.objects.filter(farm__owner=user).count(),
            'total_listings': Listing.objects.filter(seller=user).count(),
            'disease_distribution': disease_distribution,
            'recent_scans': recent_scans,
        })
