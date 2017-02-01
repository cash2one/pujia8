function SetCookie(name,value)
{
    var Days = 30;
    var exp = new Date();
    exp.setTime(exp.getTime() + Days*24*60*60*1000);
    document.cookie = name + "="+ escape (value) + ";expires=" + exp.toGMTString() + ";path=/";
}

$('#id_gallery_order_by').change(function () {
    SetCookie('gallery_order_by',$('#id_gallery_order_by').val());
    window.location.href="?gallery_order_by=" + $('#id_gallery_order_by').val() + "";
})

$('#id_order_by').change(function () {
    SetCookie('order_by',$('#id_order_by').val());
    window.location.href="?order_by=" + $('#id_order_by').val() + "";
})

$('#id_games_order_by').change(function () {
    SetCookie('games_order_by',$('#id_games_order_by').val());
    window.location.href="?games_order_by=" + $('#id_games_order_by').val() + "";
})

$('#id_games_state').change(function () {
    SetCookie('games_state',$('#id_games_state').val());
    window.location.href="?games_state=" + $('#id_games_state').val() + "";
})

$('#id_comments_order_by').change(function () {
    SetCookie('comments_order_by',$('#id_comments_order_by').val());
    window.location.href="?comments_order_by=" + $('#id_comments_order_by').val() + "";
})

$('#id_game_language').change(function () {
    SetCookie('game_language',$('#id_game_language').val());
    window.location.href="?game_language=" + $('#id_game_language').val() + "";
})

$('#id_serverid').change(function () {
    SetCookie('serverid',$('#id_serverid').val());
    window.location.href="?serverid=" + $('#id_serverid').val() + "";
})

$('#show_all_rank').click(function () {
    $(".ranking").show();
})

function background_pre(url){
    $("body").attr("style", "background-image: url("+url+");")
}

function getCookie(name) {
    var cookieStr = document.cookie;
    if(cookieStr.length > 0) {
        var cookieArr = cookieStr.split("; "); //将cookie信息转换成数组
        for (var i=0; i<cookieArr.length; i++) {
            var cookieVal = cookieArr[i].split("="); //将每一组cookie(cookie名和值)也转换成数组
            if(cookieVal[0] == name) {
                return unescape(cookieVal[1]); //返回需要提取的cookie值
            }
        }
    }
};

function at(str){
    var old = $("#id_message").val();
    $("#id_message").val(old + "@" + str + " ");
    $('html,body').animate({
        scrollTop:$('#quick_reply').offset().top},500
    );
    $("#id_message").textFocus();
}

var commentstr='提示：\n• 欢迎大家发表游戏心得或感想。\n• 言弹被5人点赞后转为“超言弹”，可获得20PP奖励。\n• 请勿灌水，内容不得少于10字。';
function comment_at(str){
    var old = $("#comment").val();
    if(old==commentstr){
           old='';
    };
    $("#comment").val(old + "@" + str + " ");
    $('html,body').animate({
        scrollTop:$('#quick_reply').offset().top},500
    );
    $("#comment").focus();
}

function a(){
    $("#top_img").attr("src", "/static/img/top2.png?v=1.02");
}
function b(){
    $("#top_img").attr("src", "/static/img/top.png?v=1.02");
}

//添加表情
var inputEmoji = document.createElement("div");
var node=document.createTextNode("添加表情");
inputEmoji.appendChild(node);
inputEmoji.className = 'btn btn-default';
inputEmoji.style.display = 'inline-block';
if (document.getElementById('reply_form')){
    var theForm = document.getElementById('reply_form');
    theForm.getElementsByTagName('p')[0].style.display = 'inline-block';
    appendEmoji();
    console.log(1);
}else if(document.getElementById('afocus')){
    var theForm = document.getElementById('afocus');
    $('div.frm-buttons').css('display','inline-block');
    appendEmoji();
    console.log(2);
}else if(document.getElementById('cform')){
    var theForm = document.getElementById('cform');
    appendEmoji();
    console.log(3);
}

function appendEmoji(){

    //theForm.getElementsByTagName('p')[0].parentNode.insertBefore(inputEmoji,theForm.getElementsByTagName('p')[0]);
    theForm.appendChild(inputEmoji);

    emojiDiv = document.createElement("div");
    emojiDiv.style.height = "auto";
    emojiDiv.style.width = "auto";
    emojiTag = document.createElement("div");
    emojiTag.style.height = "auto";
    emojiTag.style.width = "auto";

    emojiDiv.appendChild(emojiTag);

    emojiContent = document.createElement("div");
    emojiContent.style.height = "160px";
    emojiContent.style.width = "auto";
    emojiContent.style.overflow = "auto";
    emojiDiv.appendChild(emojiContent);

    $.get("/api/emoji/",function(data){
        for (var i = 0; i < data.length; i++){
            var emojiName = document.createElement("span");
            node=document.createTextNode(data[i].name);
            emojiName.appendChild(node);
            emojiName.className = data[i].name + ' btn btn-default';
            (function(name){
                emojiName.onclick = function(){
                    $('.emojiFrame').css('display','none');
                    $('#'+name).css('display','block');
                }
            })(data[i].name);
            emojiTag.appendChild(emojiName);
            var emojiFrame = document.createElement("div");
            emojiFrame.style.height = "auto";
            emojiFrame.style.width = "auto";
            emojiFrame.id = data[i].name;
            emojiFrame.className = "emojiFrame";
            for (var j=0;j<data[i].emoji_img_list.length;j++){
                var emojiImg = document.createElement("img");
                emojiImg.style.height = "80px";
                var emoji_url = data[i].emoji_img_list[j].emoji_url;
                emojiImg.src = emoji_url;
                emojiImg.title = data[i].emoji_img_list[j].description;
                emojiImg.alt = data[i].emoji_img_list[j].description;
                emojiFrame.appendChild(emojiImg);
                (function(emoji_url){
                    emojiImg.onclick = function(){
                        appendUrl(emoji_url);
                    }
                })(emoji_url);
            }
            emojiContent.appendChild(emojiFrame);
            $('.emojiFrame').css('display','none');
            $('#'+data[0].name).css('display','block');
        }

        var emojiBack = document.createElement("span");
        node=document.createTextNode("收回");
        emojiBack.appendChild(node);
        emojiBack.className = "btn btn-warning";
        emojiBack.onclick = function(){
            emojiDiv.parentNode.replaceChild(inputEmoji,emojiDiv);
        }
        emojiTag.appendChild(emojiBack);
    });
}

inputEmoji.onclick = function(){
    inputEmoji.parentNode.replaceChild(emojiDiv,inputEmoji);
}
function appendUrl(url){
    theForm.getElementsByTagName('textarea')[0].value += '\n' + url ;
}

// 表情over

/*Wrote by Sorata 20151120*/
$('#id_message,#id_content').on('keyup',function(){
    v=$(this).val();
    v=v.replace(/</g,'&lt;').replace(/>/g,'&gt;');
    /*b2strong*/
    var reg = /\[b\]([\S\u3000 ]*)\[\/b\]/img;
    v = v.replace(reg, "<strong>$1</strong>");
    /*code2pre*/
    var reg = /\[code\]([\S\s]*?)\[\/code\]/img;
    v = v.replace(reg, "<pre>$1</pre>");
    /*pic2img*/
    var reg = /((http[s]?:\/\/?[^ \f\n\r\t\v\?]*)|(\/static\/upload[s]?\/[\w]*))(\.jpg|\.jpeg|\.gif|\.png|\.bmp)/img;
    v = v.replace(reg, "<img src='$&' />");
    /*audio2audio*/
    var reg = /((http[s]?:\/\/?[^ \f\n\r\t\v\?]*)|(\/static\/upload[s]?\/[\w]*)).(mp3|wav|ogg)/img;
    v = v.replace(reg, "<audio src='$&' controls='controls'></audio>");
    /*video2video*/
    var reg = /((http[s]?:\/\/?[^ \f\n\r\t\v\?]*)|(\/static\/upload[s]?\/[\w]*)).mp4/img;
    v = v.replace(reg, "<video src='$&' controls='controls' preload='preload' width='600'></video>");
    /*link2a*/
    var reg = /\/static\/upload\/[\w]*.(zip|rar|gz|7z|apk|ipa)/img;
    v = v.replace(reg, "<a href='$&'>$&</a>");
    /*youku2iframe*/
    var reg = /http:\/\/v.youku.com\/v_show\/id_([A-Za-z0-9=]+).html(\?f=[0-9]+)?/img;
    v = v.replace(reg, "<iframe height=540 width=100% src='http://player.youku.com/embed/$&' frameborder=0 allowfullscreen></iframe>");
    /*letv2object*/
    var reg = /http:\/\/www.letv.com\/ptv\/vplay\/([A-Za-z0-9]+).html/img;
    v = v.replace(reg, "<object width='600' height='480'><param name='allowFullScreen' value='true'><param name='flashVars' value='id=$&' /><param name='movie' value='http://i7.imgs.letv.com/player/swfPlayer.swf?autoplay=0' /><embed src='http://i7.imgs.letv.com/player/swfPlayer.swf?autoplay=0' flashVars='id=$&' width='600' height='480' allowFullScreen='true' type='application/x-shockwave-flash' /></object>");
    /*tudou2object*/
    var reg = /http:\/\/www.tudou.com\/(albumplay|programs\/view|listplay)\/([A-Za-z0-9\=\_\-]+)(\/[A-Za-z0-9\=\_\-]+.html|\/(\?fr=[A-Za-z0-9\=\_\-]+)?|.html)/img;
    v = v.replace(reg, "<embed src='http://www.tudou.com/a/$2/&resourceId=0_05_02_99&iid=130747612&bid=05/v.swf' allowFullScreen='true' quality='high' width='600' height='480' align='middle' allowScriptAccess='sameDomain' type='application/x-shockwave-flash'></embed>");
    /*bilibili2embed*/
    var reg = /http:\/\/www.bilibili.(tv|com)\/video\/av([A-Za-z0-9]+)\//img;
    v = v.replace(reg, "<embed src='http://static.hdslb.com/miniloader.swf?aid=$2&page=1' allowscriptaccess='never' allowFullScreen='true' quality='high' flashvars='playMovie=true&auto=1' width='600' height='480' align='middle'  type='application/x-shockwave-flash' wmode='transparent'></embed>");
    /*acfun2object*/
    var reg = /http:\/\/www.acfun.(tv|com)\/v\/ac([A-Za-z0-9]+)/img;
    v = v.replace(reg, "<object type='application/x-shockwave-flash' data='http://static.acfun.mm111.net/player/ACFlashPlayer.out.swf' width='600' height='480'><param name='allowfullscreen' value='true'><param name='allowscriptaccess' value='always'><param name='seamlesstabbing' value='true'><param name='wmode' value='direct'><param name='allowFullscreenInteractive' value='true'><param name='flashvars' value='type=page&url=http://www.acfun.tv/v/ac$2'></object>");
    v=v.replace(/\n/g,'<br/>');
    $('#showcontent').html("<strong>实时预览：</strong><br>"+v+"<hr>");
});

// var mp3url;
// myDate = new Date();
// today=(myDate.getMonth()+1)+""+myDate.getDate();
// if(getCookie("today")!=today){
//     $.get('/pujiapi/','', function(data, status) {
//         mp3arr=data.split(",");
//         mp3l=mp3arr.length;
//         mp3url=mp3arr[parseInt(mp3l*Math.random())];
//         SetCookie("mp3url",mp3url);
//         SetCookie("today",today);
//     });
// }else{
//     mp3url=getCookie("mp3url");
// }
// function play_click(){
//     var div = document.getElementById('puji_play');
//     if($.browser.mozilla) {
//         div.innerHTML = '<object data="'+mp3url+'" type="application/x-mplayer2" width="0" height="0"><param name="src" value="'+mp3url+'"><param name="autostart" value="1"><param name="playcount" value="infinite"></object>';
//     }else{
//         div.innerHTML = '<embed src="'+mp3url+'" loop="0" autostart="true" hidden="true"></embed>';
//     }
// }

// $('#top_img').click(function(){play_click();});
$('#download').click(function (){
$('#tab li:eq(1) a').tab('show');
$('html, body').animate({scrollTop: $("#tab").offset().top-$("#tab").height()}, 500);
});
$(window).resize(function(){changeimgwidth();changerfix(1);});
$('#tab li').click(function(){changeimgwidth();});
function changeimgwidth(){
    if($.browser.msie){
        $('#game_content').removeClass('fade');
        $('#game_dl').removeClass('fade');
        $('#game_review').removeClass('fade');
    }
    var gameContentWidth=$('#tab').width();
    $('#game_content').css('width',gameContentWidth+'px');
    $('#game_dl').css('width',gameContentWidth+'px');
    $('#game_review').css('width',gameContentWidth+'px');
    changepost();
}
function changepost(){
    var postContentWidth=$('.modal-body').eq(2).width();
    $('.post').each(function(){
        pobj=$(this).find('td').eq(1).find('p').eq(0);
        if(pobj.height()>240){
            if(pobj.parent().find('.transformp').length==0){
                pobj.addClass('hidep');
                pobj.after('<p class="transformp pull-right"><a href="javascript:void(0);">展开</a></p>');
            }
        }
        $(this).find('td').eq(1).children('p').each(function(){
            $(this).children('img').each(function(){
                if($(this).width()>postContentWidth){
                    $(this).css('width','100%');
                }
            });
        });
    });
}
function changerfix(resize){
    if($('.span8').length>0 && $('#rsbar').length>0 && $('.span8').eq(0).offset().top==$('#rsbar').offset().top){
        scrollTop=$(document).scrollTop();
        rheight=$('#rsbar').height()+$('#rsbar').offset().top;
        rwidth=$('#rsbar').width();
        bheight=$(window).height();
        fheight=$('#footer').height();
        obj2=$('#recommend');
        obj1=$('#pujia_good');
        if($('.navbar-fixed-top').css('position')=='fixed'){htop=56;}else{htop=5;}
        totalheight=obj1.height()+obj2.height()+30;
        if(bheight-fheight>totalheight){hideheight=0;}else{hideheight=$('#footer').offset().top-totalheight-120;}
        if(scrollTop>rheight && (obj1.css('position')!='fixed'||resize==1)){
            $('#rsbar').css('position','relative');
            obj1.css({'position':'fixed','width':rwidth+'px','top':htop+'px'});
            obj2.css({'position':'fixed','width':rwidth+'px','top':(htop+30+obj1.height())+'px','z-index':2});
        }else if(obj1.css('position')=='fixed' && scrollTop<rheight){
            obj1.css({'position':'relative','top':'auto','width':'100%'});
            obj2.css({'position':'relative','top':'auto','width':'100%'});
        }else if(hideheight>0 && obj1.css('position')=='fixed'){
            if($('#pujia_good').offset().top>hideheight){
                obj2.css({'position':'relative','top':'auto','width':'100%'});
            }else{
                obj2.css({'position':'fixed','width':rwidth+'px','top':(htop+30+obj1.height())+'px','z-index':2});
            }
        }
    }else if(typeof(obj1) != "undefined"){
        obj1.css({'position':'relative','top':'auto','width':'100%'});
        obj2.css({'position':'relative','top':'auto','width':'100%'});
    }
}
var iframeid="gameiframe";
function fullscreen(showfull){
    iframeobj=$('#'+iframeid);
    bgpic=iframeobj.css('background-image');
    iframeobj.removeAttr('style');
    if(showfull==0){
        $('#container').removeAttr('style');
        iframeobj.closest('.modal-body').removeAttr('style');
        $('.modal-fix').removeAttr('style');
        $('#comments').show();
        $('#footer').show();
        $('.item').show();
        $('.row').eq(2).show();
        $('body').css({'background-image':bgpic,"padding-top":"60px"});
        $('#outfullscreen').remove();
    }else{
        iframewidth=iframeobj.width();
        iframeobj.css({position:"fixed",width:"100%",height:"100%",top:"39px",left:0,"background-image":$('body').css('background-image'),"z-index":"3","padding-top":"20px"});
        $('body').css({'background-image':"none","padding-top":"40px"});
        $('#container').css({position:"fixed",width:"100%",height:"100%"});
        iframeobj.closest('.modal-body').css("width","100%");
        $('.modal-fix').css({position:"fixed",width:"100%",height:"100%"});
        $('.item').hide();
        $('#comments').hide();
        $('#footer').hide();
        $('.row').eq(2).hide();
        $('.nav').eq(0).append('<li id="outfullscreen"><a href="javascript:void(0);" onclick=\'fullscreen(0)\'>退出全屏</a></li>');
    }
}
(function(){
    $('.btn-navbar').click(function(){
        if($('#'+iframeid).length>0){
            obj=$('#'+iframeid);
            if(obj.css('position')=='fixed'){
                $('#outfullscreen').remove();
                fullscreen(0);
            }
        }
    });
    if($('#modal-body .post').length==0){
        $('#modal-body').parents('.item').hide();
    }
    $(document).on("click",'.post .transformp a',function(e){
        e.preventDefault();
        tdobj=$(this).parents('td');
        p1=tdobj.find('p').eq(0);
        if($(this).html()=='展开'){
            p1.removeClass('hidep');
            $(this).html('收起');
        }else{
            p1.addClass('hidep');
            $(this).html('展开');
            window.scrollTo(0,tdobj.offset().top-48);
        }
    });
    changeimgwidth();
    $("#cform").submit(function(e){var formobj=$(this),commentobj=$("#modal-body"),mesobj=$('#comment');if(mesobj.val().length<10){alert('请勿灌水，评论内容不得少于10个字符哦');return false}if(mesobj.val()==commentstr){alert('猪头你还没写内容呢，写点什么再发表吧~');mesobj.focus();return false}$.ajax({type:"POST",url:"/comment/post/",dataType:"json",contentType:"application/x-www-form-urlencoded",data:{csrfmiddlewaretoken:$("input[name='csrfmiddlewaretoken']").val(),comment:mesobj.val(),next:$("input[name='next']").val(),path:$("input[name='path']").val()},beforeSend:function(){formobj.find('.btn-primary').attr("disabled","disabled")},success:function(data){if(data.info!=''){alert(data.info);return false}else{tmp='<table id="c'+data.cid+'" class="post"><tbody><tr><td style="text-align: center" valign="top" width="48"><img src="'+data.avatar+'" alt="\''+data.username+'\'" height="48" width="48"></td><td width="10"></td><td valign="top" width="auto"><a href="/user/'+data.uid+'/" target="_blank"><b>'+data.username+'</b></a><small class="pull-right">'+data.date+'</small><p>'+data.content+'</p><small class="pull-right">赞TA(0) <a href="javascript:comment_at(\''+data.username+'\')">@TA</a> <a href="/comment/edit/'+data.cid+'/">改TA</a></small></td></tr></tbody></table>'}if(commentobj.children('table').length>0){commentobj.children('table').eq(0).before(tmp);mesobj.val(commentstr);$("html,body").animate({scrollTop:commentobj.offset().top},500)}else{window.location.reload()}commentobj.closest('.modal-fix').find('h3').html("总言弹：<span id=\"count\">"+(parseInt($('#count').html())+1)+"</span>发");formobj.find('.btn-primary').removeAttr("disabled")},error:function(){alert('连接异常，请重试');formobj.find('.btn-primary').removeAttr("disabled");return false}});return false});
    $("#reply_form .btn-primary").click(function(e){e.preventDefault();e.stopPropagation();var formobj=$('#reply_form'),commentobj=$("#reply_list"),mesobj=$('#id_message');if(mesobj.val().length<10){alert('请勿灌水，恢复内容不得少于10个字符哦');return false}$.ajax({type:"POST",url:formobj.attr('action'),dataType:"json",contentType:"application/x-www-form-urlencoded",data:{csrfmiddlewaretoken:$("input[name='csrfmiddlewaretoken']").val(),message:mesobj.val()},beforeSend:function(){formobj.find('.btn-primary').attr("disabled","disabled")},success:function(data){if(data.info!=''){alert(data.info);return false}else{tmp='<table id="p'+data.cid+'" class="post"><tbody><tr><td style="text-align: center" valign="top" width="48"><a href="#" rel="popover" data-original-title="个人介绍"><img src="'+data.avatar+'" alt="'+data.username+'" height="48" width="48"></a></td><td width="10"></td><td valign="top" width="auto"><a href="/user/'+data.uid+'/" target="_blank">'+data.username+'</a><small class="pull-right">#'+(parseInt($('#count').html())+1)+' - '+data.date+'</small><p>'+data.content+'</p><small class="pull-right"><a href="javascript:at(\''+data.username+'\')">@TA</a> <a href="/post/'+data.cid+'/edit/">编辑</a> <a href="javascript:score(\''+data.uid+'\')">宠幸</a></small></td></tr></tbody></table>'}if(commentobj.length>0){commentobj.children('table').last().after(tmp);mesobj.val('');tmp='回复 [ <span id="count">'+(parseInt($('#count').html())+1)+'</span> ] <span class="snow">|</span> 最新回复 '+data.date;$('#comments').find('.modal-header').html(tmp)}else{window.location.reload()}formobj.find('.btn-primary').removeAttr("disabled")},error:function(){alert('连接异常，请重试');formobj.find('.btn-primary').removeAttr("disabled");return false}});return false});


    $('#comment').focus(function(){
        if($(this).val()==commentstr){
            $(this).val('');
        }
    });
    $('#comment').blur(function(){
        if($(this).val()==''){
            $(this).val(commentstr);
        }
    });
    $("#id_language").change(function(){
        if($(this).val()!='cn'){
            $('#id_team').closest('tr').hide();
            $('#id_level').closest('tr').hide();
        }else{
            $('#id_team').closest('tr').show();
            $('#id_level').closest('tr').show();
        }
    });
    $(document).scroll(changerfix);
/*modify over*/
    var isIE=!!window.ActiveXObject;
    var isIE6=isIE&&!window.XMLHttpRequest;
    if(isIE){if(isIE6){alert('您正在使用低版本浏览器，请使用Chrome、火狐、Safari等支持Html5的浏览器来访问，获得最佳的浏览效果。');}}
})();
