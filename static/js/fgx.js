

IF_MAX = 5.2e9
IF_NOM = 3.4e9

LO_MAX = 13.6e9
LO_MIN = 6.8e9


function tune_lo() {
  var my_url = "/tune_lo";
  var freq = document.getElementById("loFreq").value;
  var dat = {
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

function check_ld() {
  my_url = "/check_lock_detect";
  dat = {};

  $.ajax( {
    type: "GET",
    url: my_url,
    async: true,
    datatype: 'json',
    data: JSON.stringify(dat),
    contentType: 'application/json;charset=UTF-8',
    success: function(data) {
      console.log(data);
      },
    error: function (result) {
      console.log(result);
    }
  });
};


function autoTune() {
  var rfFreq = document.getElementById("rfFreq").value;
  var my_url = "/auto_tune";
  var dat = {
         "rf_freq": rfFreq
        };
  
  $.ajax( {
    type: "POST",
    url: my_url,
    async: true,
    datatype: 'json',
    data: JSON.stringify(dat),
    contentType: 'application/json;charset=UTF-8',
    success: function(data) {
      // console.log(data);
      document.getElementById("ifFreq").value = data.if_freq/1e9
      document.getElementById("loFreq").value = data.lo_freq/1e9
      },
    error: function (result) {
      console.log(result);
    }
  });

};

function rfChanged() {
  // var rfFreq = document.getElementById("rfFreq").value;
  // var ifFreq = document.getElementById("ifFreq").value;
  // console.log(rfFreq);  
  // console.log(ifFreq);  
};

