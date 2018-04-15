
function blink_green() {
  console.log('blink green');
  my_url = "/blinky/green";
  
  $.ajax( {
    type: "GET",
    url: my_url,
    async: true,
    success: function() {
      console.log("success");
      },
    error: function (result) {
      console.log(result);
    }
  });
};

function blink_red() {
  console.log('blink red');
  my_url = "/blinky/red";
  
  $.ajax( {
    type: "GET",
    url: my_url,
    async: true,
    success: function() {
      console.log("success");
      },
    error: function (result) {
      console.log(result);
    }
  });
};

function blink_blue() {
  console.log('blink blue');
  my_url = "/blinky/blue";
  
  $.ajax( {
    type: "GET",
    url: my_url,
    async: true,
    success: function() {
      console.log("success");
      },
    error: function (result) {
      console.log(result);
    }
  });
};

