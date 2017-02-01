// JavaScript source code
function remarkGo() {
  document.getElementById('id_dest').focus()
  recPs = $("#id_remarks > p");
  for (var i = 0; i < recPs.length; i++) {
    if (recPs[i].innerHTML != "") {
      newdiv = parseStr(recPs[i].innerHTML);
      newdiv.insertBefore(recPs[i]);
      recPs.parent()[0].removeChild(recPs[i]);
    }
  }
}
function copyText(myBtn) {
  $("#id_dest").html(
    $(myBtn).parents("#id_remarkarea").find("p").html().replace(/<br>/g, "\n"));
}

function parseStr(tarStr) {
  divE = $("<div></div>");

  strList = tarStr.split(" ");
  userName = strList[0].substr(1);
  editDate = strList[2] + " " + strList[3].substr(0, 8);
  transVal = strList[3].substr(12);

  iconA = $("<i></i>").attr("class", "icon-pencil");
  nameA = $("<a></a>").html(userName)/*.attr("class", "btn btn-info")*/.attr("href", "#id_remarks");
  leftCol = $("<div></div>").attr("class", "span2").append(iconA, "   ", nameA);

  rightCol = $("<div></div>").attr("class", "span5").attr("id", "id_remarktime")
            .append($("<small></small>").html(editDate));

  firstRow = $("<div></div>").attr("class", "row").append(leftCol, rightCol);

  copyBtn = $("<input>").attr("value", "复制").attr("class", "btn btn-info")
            .attr("onclick", "copyText(this); return false;").attr("type", "button");
  conts = $("<pre></pre>").append($("<p></p>").html(transVal));
  conts = $("<div></div>").attr("id", "id_remarkarea").attr("class", "targetArea row")
          .append($("<div></div>").attr("class", "span6").append($("<p></p>").html(transVal)))
          .append($("<div></div>").attr("class", "span1 buttonArea").append(copyBtn));

  divE.append(firstRow, conts);
  return divE;
}