<?php
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json; charset=UTF-8");

$json = '[{"date":"2014-11-11 12:45:34","value":"99"}]';


//echo $data[0]["username"];

if (isset($_GET["json"])) {
//if (isset($json)) {

try{
	$data = json_decode(stripslashes($_GET["json"]), TRUE);
	//$data = json_decode($json, TRUE);
	
	echo $_GET["json"]."<br>";
	
	echo stripslashes($_GET["json"]);
	echo $data[0]["value"];
	
	$db = new PDO('mysql:host=mysql12.000webhost.com;dbname=a1206683_temp;charset=utf8', 'a1206683_temp', 'jakkarakeitto');
	//$db = new PDO('mysql:host=localhost;dbname=test', 'root', '');
	
	$db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
	
	
	for($x = 0; $x < count($data); $x++)
	{
		
		$stmt = $db->prepare("INSERT INTO temp(date, value) VALUES(:date,:value)");
		$stmt->bindValue(':date', $data[$x]["date"], PDO::PARAM_STR);
		$stmt->bindValue(':value', $data[$x]["value"], PDO::PARAM_STR);
		$stmt->execute();
	}
	
	echo "success";
}
catch(PDOException $ex){
	echo $ex->getMessage();
	
}
}
 ?>