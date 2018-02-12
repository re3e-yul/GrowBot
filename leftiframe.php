<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<html>
	<head>
        	<meta http-equiv="content-type" content="text/html; charset=utf-8"/>
	        <title></title>
        	<meta name="generator" content="LibreOffice 5.1.2.2 (Linux)"/>
	        <meta name="created" content="2016-05-20T11:55:46.753782914"/>
        	<meta name="changed" content="00:00:00"/>
	        <style type="text/css">
        	        @page { margin: 2cm }
                	p { margin-bottom: 0.25cm; line-height: 120% }

	

		.myButton {
			-moz-box-shadow: 0px 10px 14px -7px #276873;
			-webkit-box-shadow: 0px 10px 14px -7px #276873;
			box-shadow: 0px 10px 14px -7px #276873;
			background:-webkit-gradient(linear, left top, left bottom, color-stop(0.05, #599bb3), color-stop(1, #408c99));
			background:-moz-linear-gradient(top, #599bb3 5%, #408c99 100%);
			background:-webkit-linear-gradient(top, #599bb3 5%, #408c99 100%);
			background:-o-linear-gradient(top, #599bb3 5%, #408c99 100%);
			background:-ms-linear-gradient(top, #599bb3 5%, #408c99 100%);
			background:linear-gradient(to bottom, #599bb3 5%, #408c99 100%);
			filter:progid:DXImageTransform.Microsoft.gradient(startColorstr='#599bb3', endColorstr='#408c99',GradientType=0);
			background-color:#599bb3;
			-moz-border-radius:8px;
			-webkit-border-radius:8px;
			border-radius:8px;
			display:inline-block;
			cursor:pointer;
			color:#ffffff;
			font-family:Arial;
			font-size:20px;
			font-weight:bold;
			padding:13px 32px;
			text-decoration:none;
			text-shadow:0px 1px 0px #3d768a;
		}
		.myButton:hover {
			background:-webkit-gradient(linear, left top, left bottom, color-stop(0.05, #408c99), color-stop(1, #599bb3));
			background:-moz-linear-gradient(top, #408c99 5%, #599bb3 100%);
			background:-webkit-linear-gradient(top, #408c99 5%, #599bb3 100%);
			background:-o-linear-gradient(top, #408c99 5%, #599bb3 100%);
			background:-ms-linear-gradient(top, #408c99 5%, #599bb3 100%);
			background:linear-gradient(to bottom, #408c99 5%, #599bb3 100%);
			filter:progid:DXImageTransform.Microsoft.gradient(startColorstr='#408c99', endColorstr='#599bb3',GradientType=0);
			background-color:#408c99;
		}
		.myButton:active {
			position:relative;
			top:1px;
		}





	        </style>
		</head>


	<?php
	echo(date("H:i:s") . "<br>");
	exec("pgrep Gr", $output, $return);
	echo "PID: $output[0]";

	if (isset($_POST['TrigPoint']))
	{
        	$MoistTrig = $_POST['TrigPoint'];
		$file = '/var/www/GTTrig.log';
		file_put_contents($file, $MoistTrig);
	}
	?>
	

	<body lang="en-CA" dir="ltr">
	<tr><center>
        	<form method="get" action="leftiframe.php">
				<br>
				<input type="submit" value="ON/OFF" name="OnOff"></a><br><br><br>
                                <input type="submit" value="Light Test" name="LightTest"><br><br><br>
                                <input type="submit" value="Pump Test" name="PumpTest"><br><br>
                                
                </form></tr></center>
                <form method="post" action="leftiframe.php">
                                <br><center>Soil moiture triger point <br/>
				<INPUT TYPE = "Text" NAME = "TrigPoint" size="4"><br/>
                </form></tr></center>


		<?php
		exec("pgrep Gr", $output, $return);
		if ($return == 0) {
		 	if(isset($_GET['OnOff'])){
				exec("pgrep Gr)", $output, $return);
				$ShellSTR = "sudo kill -KILL $output[0]";
                        	$command = escapeshellcmd("$ShellSTR");
                        	$output = shell_exec($command);
								
			}
		}else {
    			if(isset($_GET['OnOff'])){
                                $ShellSTR = "sudo /var/www/GrowBot5.py -v";
                                $command = escapeshellcmd("$ShellSTR");
                                $output = shell_exec($command);
                        }
		}
		
		if(isset($_GET['LightTest'])){
                        $ShellSTR = "sudo /var/www/LightTest.py";
                        $command = escapeshellcmd("$ShellSTR");
                        $output = shell_exec($command);
                }
		if(isset($_GET['PumpTest'])){
                        $ShellSTR = "sudo /var/www/PumpTest.py";
                        $command = escapeshellcmd("$ShellSTR");
                        $output = shell_exec($command);
                }
                ?>
		</label>
	</body>
</html>
