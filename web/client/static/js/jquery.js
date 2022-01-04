$(document).ready(function () {

  $(".closet1").click(function () {
    $(".type1").prop("checked", true);
  })

  $(".closet2").click(function () {
    $(".type2").prop("checked", true);
  })

  $(".closet3").click(function () {
    $(".type3").prop("checked", true);
  })

  $(".closet-type-box").click(function () {
    $(this).addClass("open").siblings().removeClass("open")

  })






});
