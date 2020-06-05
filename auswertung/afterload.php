<?php
session_start();
require "config.ini.php";

$hash = hash('sha256',utf8_encode($web_passwort));

if(!isset($_SESSION['login'])){
    if($_POST['passwort'] !== $hash){
  exit;
}}

//get connection
$mysqli = new mysqli($DB_HOST, $DB_USERNAME, $DB_PASSWORD, $DB_NAME);

if(!$mysqli){
  die("Connection failed: " . $mysqli->error);
}

if(!isset($_POST['output'])){
  $_POST['output'] ="none";
}

if($_POST['output']=== "json" ){
        
  $_SESSION['login']="true";
  $sql = "SHOW COLUMNS FROM $tabellenname_ueberischt";
  $res = $mysqli->query($sql);
  $columns=array();
  while($row = $res->fetch_assoc()){
        $columns[] = $row['Field'];}
      print json_encode($columns);
      
    
        $res->close();
        exit;
    }

if($_POST['output']=== "html"){
        $_SESSION['login']="true";
        $sql = "SHOW COLUMNS FROM $tabellenname_ueberischt";
        $res = $mysqli->query($sql);
        echo '<select id="spaltenauswahl" multiple size="8">';
        $columns=array();
        
        while($row = $res->fetch_assoc()){
            $columns[] = $row['Field'];

            if($row['Field'] !== "id" && $row['Field'] !== "trip_nummer" && $row['Field'] !== "tag" && $row['Field'] !== "uhrzeit_Beginns"&& $row['Field'] !== "uhrzeit_Ende"&& $row['Field'] !== "kmstand_start"){
            echo '<option value="'.$row["Field"].'">'.$row["Field"].'</option>';
            }
        }
        echo '</select>';
        $res->close();
    }
    
    else{


      if(isset($_POST['beginn'])){
      $beginn_html =$_POST['beginn'];}
      else{
        $beginn_html = '1970-01-01';
      }
      if(isset($_POST['ende'])){
        $ende_html = $_POST['ende'];
      }
      else{
        $ende_html = "2030-01-01";
      }


  //query to get data from the table
  $query = "SELECT * FROM $tabellenname_ueberischt where tag BETWEEN '$beginn_html' AND '$ende_html' ORDER BY tag, uhrzeit_Beginns ;";

  //execute query
  $result = $mysqli->query($query);
  //loop through the returned data
  $data = array();
  foreach ($result as $row) {
    $data[] = $row;
  }


  //free memory associated with result
  $result->close();

  //close connection
  $mysqli->close();

  //now print the data
  print json_encode($data);

}
     ?>