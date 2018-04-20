
function tune_lo() {
  my_url = "/tune_lo";
  freq = document.getElementById("loFreq").value;
  dat = {
         "freq": freq
        };
  
  $.ajax( {
    type: "POST",
    url: my_url,
    async: true,
    datatype: 'json',
    data: JSON.stringify(dat),
    contentType: 'application/json;charset=UTF-8',
    success: function() {
      console.log("success");
      },
    error: function (result) {
      console.log(result);
    }
  });
};


