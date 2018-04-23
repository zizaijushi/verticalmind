$(document).ready(function () {
	function wcropper(dom) {
		dom.cropper({
			aspectRatio: 9 / 9,
			crop: function (event) {
				console.log(event.detail.x);
				console.log(event.detail.y);
				console.log(event.detail.width);
				console.log(event.detail.height);
				console.log(event.detail.rotate);
				console.log(event.detail.scaleX);
				console.log(event.detail.scaleY);
			}
		});
	}

	function readURL(input,dom) {
		if (input.files && input.files[0]) {
			var reader = new FileReader();
			reader.onload = function (e) {
				dom.attr('src', e.target.result);
				dom.cropper({
				    reset: function(){}
				})
			}
			reader.readAsDataURL(input.files[0]);
		}
	}

	var img = $('#head-img');
	var imgPar = $('#head-img-col');
	wcropper(img);
	$("#imgInp").change(function () {
		readURL(this,img);
		new Cropper(img, {
			ready: function () {
				this.cropper.reset()
			}
		});
	});
});