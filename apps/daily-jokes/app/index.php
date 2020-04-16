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
        font: 16px/1.5 Arial, sans_serif;
    }
    </style>
  </head>
  <body>
    <div id="main_widget">
     <?php
        function get_joke() {
            $txt = file_get_contents('http://www.hahaha.de/witze/zufallswitz.txt.php');
            $doc = new DOMDocument();
            $doc->loadHTML($txt);
            $div = $doc->getElementsByTagName('div')->item(0); # get the div
            $joke = $div->firstChild->textContent; # read the text without the span
            return trim($joke);
        }
        
        function fit_font_size($text, $start, $max_height, $max_width) {
            $X = $start;
            $chars =  strlen($text);
            
            for (; $X < 60; $X+=2) {
                $text_width = ceil(0.5 * $X * $chars);
                $lines = ceil($text_width / $max_width);
                $text_height = ceil($lines*$X + ($lines-1)*0.5*$X);
                
                if ($text_height > $max_height) {
                    break;
                }
            }
            
            return ($X-2);
        }
        
        function print_joke($font_size, $joke) {
            echo '<span style="font-size:' . strval($font_size) . 'px;">' . $joke . '</span>';
        }
        
        $joke = get_joke();
        $font_size = fit_font_size($joke, 16, 600, 800);
        print_joke($font_size, $font_size);
     ?>
    </div>
  </body>
</html>