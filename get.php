<?php
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json; charset=UTF-8");

require('conn.php');

$sql = "select * from temp";
$result = mysqli_query($connection, $sql) or die("Error in Selecting " . mysqli_error($connection));

$array = array();
$onko = false;

echo '{"temp":[';
while($row =mysqli_fetch_assoc($result))
{
	if($onko){echo ",";}
	$array["value"] = $row["value"];
	$array["date"] = $row["date"];
	
	echo json_encode($array);
	$onko = true;
}

echo "]}";


mysqli_close($connection);

?>