function topDescription() {
    return $('.add-new-post textarea').val();
}

function mediaData() {
    return $('#upload-image').attr('src');
}

function addPost() {
    var template = `<article class="single-post">
						<div class="post-header">
							<img class="img-circle" src="https://scontent-waw1-1.xx.fbcdn.net/v/t1.0-1/p40x40/14100305_1759855060897943_7844781317309267984_n.jpg?oh=0b3187675c04f0d726e9ec3092b5dda1&oe=5A97F106">
							<p><strong>Group Name</strong> <em>share some info from</em> <strong>User Name</strong></p>
							<span class="post-time"><em>1 hour</em></span>
						</div>
						<div class="post-content">
							<div class="post-top-description">` + topDescription() + `</div>
							<div class="post-media-content"><img src="` + mediaData() + `"></div>
						</div>
						<div class="post-footer">
							<button class="btn btn-default btn-like">
								<span class="glyphicon glyphicon-thumbs-up"></span>Like
							</button>
							<button class="btn btn-default btn-comment">
								<span class="glyphicon glyphicon-edit"></span>Comment
							</button>
							<button class="btn btn-default btn-share">
								<span class="glyphicon glyphicon-share-alt"></span>Share
							</button>
						</div>
						<div class="likes-block">
							<span class="glyphicon glyphicon-thumbs-up"></span>
							<span class="likes-number">0</span>
						</div>
						<div class="post-comment">
							<img class="img-circle" src="https://scontent-waw1-1.xx.fbcdn.net/v/t1.0-1/p40x40/14100305_1759855060897943_7844781317309267984_n.jpg?oh=0b3187675c04f0d726e9ec3092b5dda1&oe=5A97F106">
							<textarea placeholder="Add some comment"></textarea>
							<div class="btn-group">
								<span class="glyphicon glyphicon-camera"></span>
								<span class="glyphicon glyphicon-user"></span>
								<span class="glyphicon glyphicon-save"></span>
							</div>
						</div>
					</article>`;
    return template;
}

function getComment(element) {
    return $(element).parents('.single-post').find('.post-comment textarea').val();
}

function addComment(cont) {
    var template = `<div class="comment">
						<div class="comment-photo">
							<img class="img-circle" src="https://scontent-waw1-1.xx.fbcdn.net/v/t1.0-1/p40x40/14100305_1759855060897943_7844781317309267984_n.jpg?oh=0b3187675c04f0d726e9ec3092b5dda1&oe=5A97F106">
						</div>
						<div class="comment-content">
							<span class="comment-author">Name Surname</span>
							<span class="author-content">` + getComment(cont) + `</span>
							<div class="comment-buttons">
								<span>Like</span>
								<span>Answer</span>
							</div>
						</div>	
					</div>`;
    return template;
}


$(document).ready(function () {
    var ajax_response;
    //// addPost
    $('.btn-add-post').click(function () {
        // var post = addPost()
        // var url = '/add_post'
        // sendData(url,post)
        $('.posts').prepend(post);
    });
    //// upload image preview
    document.getElementById("files").onchange = function () {
        var reader = new FileReader();

        reader.onload = function (e) {
            // get loaded data and render thumbnail.
            document.getElementById("upload-image").src = e.target.result;
        };

        // read the image file as a data URL.
        reader.readAsDataURL(this.files[0]);

        $('#upload-image').addClass('active');
    };
    //// likes
    $(document).on("click", ".btn-like", function (ev) {
        ev.preventDefault();
        var target = $(ev.target);
        var id = target.closest('.single-post').attr('id');
        console.log(id);
        var url = '/add_like'
        var data = {'id':id}
        $.ajax({type: "POST",
            url: url,
            dataType: "json",
            contentType: 'application/json;charset=UTF-8',
            data: JSON.stringify(data, null, '\t'),
            success: function (jsondata) {
            console.log(jsondata)
            var currentVal = target.parent().next().find('.likes-number').html();
            target.parent().next().find('.likes-number').html(++currentVal);
            }
            });

        });

    // $(document).on("click", ".btn-like", function (ev) {
    //     ev.preventDefault();
    //     var target = $(ev.target);
    //     var id = target.closest('.single-post').attr('id');
    //     console.log(id);
    //     var url = '/add_like'
    //     var data = {'id':id}
    //     var response = sendData(url,data)
    //     console.log(response);
    //     var currentVal = $(this).parent().next().find('.likes-number').html();
    //     $(this).parent().next().find('.likes-number').html(++currentVal);
    //     });

    // $('.btn-like').click(function () {
    //     var url = '/add_like'
    //
    //     sendData(url,post)
    //     console.log('btn-like')
    //     var currentVal = $(this).parent().next().find('.likes-number').html();
    //     $(this).parent().next().find('.likes-number').html(++currentVal);
    // });
    //// addComment
    $('.btn-add-comment').click(function () {
        var url = '/add_comment'
        var postID = $(this).parent().parent().parent().parent().attr('id')
        var textComment = getComment(this)
        var author = '';

        data = {
            'postID': postID,
            'textComment': textComment,
            'author': author
        }
        var status = sendData(url, data)
        // console.log($(this).parent().parent().parent().parent().attr('id'))
        $(this).parent().parent().parent().find(".comments").prepend(addComment(this));
        $('.post-comment textarea').val("");
    });


function sendData(url, data) {
    $.ajax({
        type: "POST",
        url: url,
        dataType: "json",
        contentType: 'application/json;charset=UTF-8',
        data: JSON.stringify(data, null, '\t'),
        success: function (jsondata) {
            // console.log(jsondata)
            ajax_response = jsondata;
            // console.log(response)


        }
    });

return ajax_response
}


});