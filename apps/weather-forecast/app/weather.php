<!DOCTYPE html>
<html>
  <head>
    <link rel="stylesheet" href="weather-icons/css/weather-icons.css">
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
    
    /* WEATHER OF TODAY: CITY */
    #main_today_city {
        background-color: rgb(153, 102, 153);
        position: absolute;
        left: 10px;
        top: 10px;
        font-size: 36px;
        font-weight: bold;
        font-style: normal;
        margin: 0px;
        text-align: left;
        width:100px;
    }
    
    #main_today_temperature {
        background-color: rgb(153, 152, 153);
        position: absolute;
        right: 50%;
        top: 10px;
        text-align: right;
        font-size: 36px;
        font-weight: bold;
        font-style: normal;
        margin: 0px;
        width:100px;
    }
    
    /* WEATHER OF TODAY: SHORT OVERVIEW */
    #main_today_short, #main_today_details {
        height: 230px;
    }
    #main_today_short {
        background-color: rgb(153, 102, 255);
        float: left;
        width: 50%;
        text-align: center;
    }
    #weather_image {
        height: 200px;
        margin: 20px 0px 0px 0px;
        font-size: 10em;
        display: block;
        margin-left: 55px;
        /*margin-right: auto;*/
        font-style: light;
        background-color:#ddd;
    }
    #main_weather_date {
        margin: 0px;
        font-size: 1.6em;
        font-weight: bold;
        display: block;
        margin-left: auto;
        margin-right: auto;
        background-color:#ddd;
    }
    /* WEATHER OF TODAY: DETAILS */
    #main_today_details {
        background-color: rgb(153, 102, 100);
        float: right;
        width: auto;
        padding: 10px;
        font-size: 1.6em;
        font-weight: bold;
        line-height: 1.5;
    }
    #main_today_details i {
        font-size: 1.6em;
    }
    
    /* WEATHER FORECAST */
    #main_forecast {
        position: relative;
        background-color: rgb(153, 102, 50);
        float: left;
        width: 100%;
        height: 330px;
        margin-top: 10px;
    }
    
    #main_forecast,#main_today_temperature, #main_today_details, #main_today_short, #main_weather_date, #weather_image, #main_today_city  {
        background-color:#ddd;
    }
    </style>
    <?php    
    function responseWeather($city, $key, $type) {
        $url = 'https://api.openweathermap.org/data/2.5/'.$type.'?q='.urlencode($city).',de&appid='.urlencode($key);
        //echo $url.'</br>';
        $curl = curl_init();
        $headers = array();
        curl_setopt($curl, CURLOPT_HTTPHEADER, $headers);
        curl_setopt($curl, CURLOPT_HEADER, 0);
        curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($curl, CURLOPT_URL, $url);
        curl_setopt($curl, CURLOPT_TIMEOUT, 30);
        $json = curl_exec($curl);
        curl_close($curl);
        $data = json_decode($json);
        return $data;
    }
    
    function getDateStr($date) {
        $tage = array("Sonntag","Montag","Dienstag","Mittwoch","Donnerstag","Freitag","Samstag");
        $months = array("Januar","Februar","März","April","Mai","Juni","Juli","August","September","Oktober","November","Dezember");
        $weekday = $tage[date("w", $date)];
        $months = $months[date("n", $date) - 1];
        $day = date('j', $date);
        return $weekday.', '.$day.'. '.$months;
    }
    
    function kelvin2degree($kelvin) {
        return round($kelvin-273.15, 0);
    }
    
    function getWeatherClass($id) {
        return 'wi wi-owm-'.$id;
    }
    
    function prepareData($forecast, $bins) {
        $weekday = array('So','Mo','Di','Mi','Do','Fr','Sa');
        $max_elements = min(count($forecast->list), $bins);
        
        for ($i = 0; $i < $max_elements; $i++) { 
            $temp = kelvin2degree($forecast->list[$i]->main->temp);
            $time = $forecast->list[$i]->dt;
            $rain = 0;
            if (property_exists($forecast->list[$i], 'rain')) {
                if (property_exists($forecast->list[$i]->rain, '3h')) {
                    $rain = round($forecast->list[$i]->rain->{'3h'}, 1);
                }                
            }
            $hour = date("H", $time);
            
            
            $data[] = array("temp" => $temp, 
                            "time" => $time, 
                            "image_id" => $forecast->list[$i]->weather[0]->id,
                            "rain" => $rain, 
                            "hour" => date("G", $time), 
                            "day" => $weekday[date("w", $time)]);
        }
        return $data;
    }
    
    function getMaxTemp($data) {
        $max = 0;
        foreach($data as $dat) {
            if($dat["temp"] > $max) {
                $max = $dat["temp"];
            }
        }
        return $max;
    }
    
    function getMinTemp($data) {
        $min = 99;
        foreach($data as $dat) {
            if($dat["temp"] < $min) {
                $min = $dat["temp"];
            }
        }
        return $min;
    }
    
    function getMaxRain($data) {
        $max = 0;
        foreach($data as $dat) {
            if($dat["rain"] > $max) {
                $max = $dat["rain"];
            }
        }
        return $max;
    }
    function getTempBars($data, $weight, $height) {
        $dist_bar = $weight / (count($data) + 0.5);
        $temp_max = getMaxTemp($data);
        $temp_min = getMinTemp($data);
        $rain_max = getMaxRain($data);
        $dist_top = 20;
        $max_temp_bar_height = 166;//$height / 2.0 - $dist_top; 
        
        for ($i = 0; $i < count($data); $i++) { 
            /* TEMPERATURE BAR */
            $bar_height = $max_temp_bar_height / ($temp_max - $temp_min);
            $bar_height = round(($data[$i]["temp"] - $temp_min) * $bar_height);
            $top = $max_temp_bar_height - $bar_height + $dist_top;
            $left = $dist_bar * ($i + 0.5);
            $style = 'height: '.$bar_height.'px; top: '.$top.'px; left: '.$left.'px; ';
            $bar = '<div style="position: absolute; border: 2px solid black; width: 6px; background-color: rgb(0, 0, 0); margin: 0px; '.$style.'"></div>';
            echo $bar;
            
            /* WEATHER ICON */
            $top = 195;
            $left = $dist_bar * ($i + 0.5) - 8;
            $img_class = getWeatherClass($data[$i]["image_id"]);
            $img = '<p class="'.$img_class.'" style="position: absolute; text-align: center; font-size: 28px; vertical-align: middle; top: '.$top.'px; left: '.$left.'px; width: 30px; height: 20px; margin: 0px;"/>';
            echo $img;
            
            /* TIME */
            $top = 230;
            $left = $dist_bar * ($i + 0.5) - 10;
            $weight = "";
            if ((int)$data[$i]["hour"] != 2) {
                $content = $data[$i]["hour"].'h';
            } else {
                $content = $data[$i]["day"];
                $weight = "font-weight: bold;";
            }
            $time = '<p style="position: absolute; top: '.$top.'px; left: '.$left.'px; width: 30px; height: 24px; text-align: center; font-size: 24px; vertical-align: middle; margin: 0px;'.$weight.';">'.$content.'</p>';
            echo $time;
            
            /* TEMPERATURE */
            $top = $max_temp_bar_height - $bar_height - 10;
            $left = $dist_bar * ($i + 0.5) - 8;
            $temp = '<p style="position: absolute; top: '.$top.'px; left: '.$left.'px; width: 30px; height: 24px; text-align: center; font-size: 24px; vertical-align: middle;margin: 0px;">'.$data[$i]["temp"].'&deg;</p>';
            echo $temp;
            
            /* WATER BAR */
            if ($data[$i]["rain"] > 0) {
                $max_rain_bar_height = 40;
                $bar_height = $max_rain_bar_height / $rain_max;
                $bar_height = round($data[$i]["rain"] * $bar_height);
                $top = 260;
                $left = $dist_bar * ($i + 0.5);
                $bar = '<div style="position: absolute; border: 2px solid black; width: 6px; background-color: rgb(0, 0, 0); margin: 0px; height: '.$bar_height.'px; top: '.$top.'px; left: '.$left.'px; "></div>';
                echo $bar;
                
                $top = $top + $max_rain_bar_height + 6;
                $left = $dist_bar * ($i + 0.5) - 10;
                $rain = '<p style="position: absolute; top: '.$top.'px; left: '.$left.'px; width: 30px; height: 24px; text-align: center; font-size: 24px; vertical-align: middle; margin: 0px">'.$data[$i]["rain"].'</p>';
                echo $rain;
            }
        }
    }
    $city = 'Koblenz'; /* set default value */
    $bins = 16; /* set default value */
    $key = '';
    
    if (isset($_GET['city'])) {
        $city = $_GET['city'];
    }
    
    if (isset($_GET['bins'])) {
        $bins = $_GET['bins'];
        $bins = max(8, min(24, $bins));
    }
    
    if (isset($_GET['key'])) {
        $key = $_GET['key'];
        
        $today = responseWeather($city, $key, 'weather');
        $forecast = responseWeather($city, $key, 'forecast');
        $data = prepareData($forecast, $bins);
        
        $weight = 800;
        $height = 600;
    } else {
       echo "<h1>ERROR: Openweather API key is missing</h1><p>Webadress should look like: weather.php?city=Koblenz&bins=16&key=[ENTER YOUR KEY HERE]</p>";
       exit();
    }
    ?>
  </head>
  <body>
    <div id="main_widget">
        <div id="main_today_short"> 
            <p id="weather_image" class="<?php echo getWeatherClass($today->weather[0]->id); ?>"/>
            <p id="main_weather_date"><?php echo getDateStr($today->dt); ?></p>
        </div>
        <p id="main_today_city"><?php echo $today->name; ?></p>
        <p id="main_today_temperature"><?php echo kelvin2degree($today->main->temp).'&deg;'; ?></p>
        <div id="main_today_details">
            <table align="center">
                <tr>
                    <td><i class="wi wi-humidity"></i></td>
                    <td align="right" id="humidity"><?php echo $today->main->humidity; ?></td><td>%</td>
                    <td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td>
                    <td><i class="wi wi-barometer"></i></td>
                    <td align="right" id="pressure"><?php echo $today->main->pressure; ?></td><td>hPa</td>
                </tr>
                <tr>
                    <td><i class="wi wi-small-craft-advisory"></i></td>
                    <td align="right" id="windspeed"><?php echo $today->wind->speed; ?></td><td>m/s</td>
                    <td>&nbsp;</td>
                    <td><i class="wi wi-cloud"></i></td>
                    <td align="right" id="clouds"><?php echo $today->clouds->all; ?></td><td>%</td>
                </tr> 
                <tr><td>&nbsp;</td><td/><td/><td/><td/><td/><td/></tr> 
                <tr><td>&nbsp;</td><td/><td/><td/><td/><td/><td/></tr> 
                <tr>
                    <td><i class="wi wi-sunrise"/></td>
                    <td align="right" id="sunrise"><?php echo date('G:i', $today->sys->sunrise); ?></td><td>Uhr</td>
                    <td/>
                    <td><i class="wi wi-sunset"/></td>
                    <td align="right" id="sunset"><?php echo date('G:i', $today->sys->sunset); ?></td><td>Uhr</td>
                </tr>
            </table>
        </div>
        <div id="main_forecast"><?php getTempBars($data, $weight, $height); ?></div>
    </div>
  </body>
</html>