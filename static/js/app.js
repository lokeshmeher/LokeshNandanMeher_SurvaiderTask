'use strict';

var app = angular.module('hotels', []);

app.controller('ReviewsController', ['$scope', '$http', function($scope, $http) {
	$scope.currentIndex = 0;
	$scope.reviewsPerFetch = 10;
	$scope.dataExhausted = false;
	$scope.reviewList = [];

	var getReviews = function() {
		$scope.isLoading = true;
		console.log('/api/get_reviews/' + $scope.hotelId + '/' + $scope.currentIndex + '/' + $scope.reviewsPerFetch);
		$http({
			method: 'GET',
			url: '/api/get_reviews/' + $scope.hotelId + '/' + $scope.currentIndex + '/' + $scope.reviewsPerFetch,
		}).then(function(response) {
			angular.forEach(response.data.reviews, function(value) {
				$scope.reviewList.push(value);
			});
			$scope.dataExhausted = response.data.dataExhausted;
			$scope.isLoading = false;
		}, function() {
			$scope.isLoading = false;
		});
	}

	$scope.$watch('hotelId', function() {
		getReviews();
	});

	$scope.getMoreReviews = function() {
		if (!$scope.dataExhausted) {
			$scope.currentIndex += $scope.reviewsPerFetch;
			getReviews();
		}
	};
}]);

app.directive('infscroll', function() {
	return {
		restrict: 'A',
		link: function(scope, element, attrs) {
			element.bind('scroll', function() {
				if ((element[0].scrollTop + element[0].offsetHeight) == element[0].scrollHeight) {
					// scroll reach to end
					scope.$apply(attrs.infscroll);
				}
			});
		}
	};
});
