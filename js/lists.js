$(function()
{
	var strs = [ "To", "Be", "Filled", "In" ];
	var list = document.getElementById("ul1");
	for (var i in strs) {
	  var para = document.createElement("p");
	  para.innerText = strs[i];

	  var elem = document.createElement("li");
	  elem.appendChild(para);
	  list.appendChild(elem);
	}
});