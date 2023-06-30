<!DOCTYPE html>
<html>
<head>
 <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">

 <style>
    body {
            font-family: Arial, sans-serif;
        }

        .menu {
            background-color: #f1f1f1;
            width: 200px;
            padding: 20px;
            position: fixed;
            top: 0;
            left: 0;
            height: 100vh;
            transition: transform 0.3s;
            z-index: 999;
        }

        .menu-button {
            position: fixed;
            top: 20px;
            left: 20px;
            font-size: 24px;
            cursor: pointer;
            z-index: 999;
        }

        .menu-button i {
            display: block;
            margin-bottom: 5px;
        }

        .menu-items {
            list-style: none;
            padding: 0;
            margin: 0;
        }

        .menu-item {
            margin-bottom: 10px;
        }

        .menu-item a {
            display: block;
            padding: 5px 0;
            text-decoration: none;
            color: black;
        }

        .menu-item a:hover {
            color: blue;
        }

        @media (max-width: 768px) {
            .menu {
                transform: translateX(-100%);
            }
        }

        .button-container {
        display: flex;
        justify-content: center;
        margin-top: 20px; /* Added margin to separate from the text above */
    }

    .button-container button {
        margin: 0 10px; /* Adjust the margin as desired */
    }


    .text-above {
        text-align: center;
        margin-bottom: 20px; /* Added margin to separate from the buttons */
    }

    ul {
      list-style-type: none;
      cursor: pointer;
    }
    li {
      padding: 5px;
      margin: 5px;
      background-color: lightgray;
      border-radius: 5px;
    }

</style>
</head>
<body>

<div class="menu">
        <ul class="menu-items">
           <br><br> <li class="menu-item"><a href="/main?account={{ result.account }}">NOVO WALLET</a></li>
            <li class="menu-item"><a href="/contract_unspent/{{ result.account }}">TOKENS / NFT BALANCE</a></li>
            <li class="menu-item"><a href="/transaction_history?account={{ result.account }}"> HISTORY ACTIVITY </a></li>
            <li class="menu-item"><a href="#">SETTINGS</a></li>
        </ul>
</div>
<div class="menu-button" onclick="toggleMenu()">
        <i class="fas fa-bars"></i>
    </div>


    <script src="https://kit.fontawesome.com/a076d05399.js" crossorigin="anonymous"></script>
    <script>
        function toggleMenu() {
            var menu = document.querySelector('.menu');

            if (menu.style.transform === 'translateX(-100%)') {
                menu.style.transform = 'translateX(0)';
            } else {
                menu.style.transform = 'translateX(-100%)';
            }
        }
    </script>


</body>
</html>