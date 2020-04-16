 <!DOCTYPE html>
<html>
  <head>
    <link rel="stylesheet" href="font_style.css">
    <style type="text/css">    
    #main_widget {
        position: relative;
        background-color: #ddd;
        width: 800px;
        height: 600px;
        margin: 5px 0px;
        font-family: "Ubuntu", "Times New Roman";
    }
    </style>
  </head>
  <body>
    <div id="main_widget">
    
     <?php
      $txt = file_get_contents(
        'http://www.hahaha.de/witze/zufallswitz.txt.php'
      );
      //echo $txt;
      $joke = strstr($txt, '<div id="zufallswitz">');
      echo $joke;
      $joke = strstr($joke, '<span id="zufallslink">', true);
      //echo $joke;
     ?>
    </div>
  </body>
</html>