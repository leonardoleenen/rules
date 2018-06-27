# Sinopsis

La capa de secure_service permite validar las peticiones que llegan a Moorea. Todas las peticiones de moorea estan expuestas como servicios web REST. 
Estos servicios son expuestos desde el backend para que aplicaciones de terceros puedan hacer uso de ellos. Todos los servicios tienen como retorno 
un mensaje de tipo  JSON 

# HandShake 

El primer paso para poder utilizar los servicios de Moorea es contar con un token valido y vigente. Este token se genera posterior al momento del login. 

Para poder crear un token es indispensable contar con dos cosas: 1) Debe ser una aplicacion de confianza quien realice la creacion del mismo y 2) se deben suministrar datos en un servicio POST los cuales se mencionan a continuacion: 

El servicio que se debe invocar es: <pre> /security/token/create</pre> mediante un metodo POST con la siguiente informacion de contexto dentro del raw data del envio: 

<pre>
	{
		"user_id":"albertoperez",
		"uuid":"453-af134-25245asd-1342342",
		"email":"albertoperez@yahoo.com",
		"profile":"cn=org",
		"app_context":"aplicacion1"
	}
</pre> 

De los datos anteriormente mencionados solo son relevantes: 

uuid, el cual hace referencia al identificador primario del sistema que ha realizado la identificación de la persona. Este ID debe ser unico e irrepetible. Sirve ademas para poder identificar a la persona univocamente. 
El userid es una informacion casi trivial. En algunas implementaciones el user_id y el uuid GENERALMENTE es el mismo atributo. 

El atributo profile indica en forma de arbol cual es el perfil o rol de la persona dentro del app_context indicando. Es decir, que este atributo actua en forma conjunta con app_context para analizar
los permisos que posee el usuario para una aplicacion determinada. 

El atributo app_context hace referencia a la aplicacion sobre la cual se esta operando. Es importante mencionar que este atributo es el reponsable de realiza un corte fisico en los datos 
que se terminan mostrando al usuario. 

Como resultado el proceso de creacion de token devuelve un JSON con los datos suministrados y el token creado el cual es un uuid que representa los datos del mismo. 

# Arquitectura

Un usuario solicita la creacion de un token para poder acceder a los servicios. En caso de no existir o no poseer un token valido el metodo de negocio eleva una excepcion 
la cual es capturada por la capa de presentacion la cual presenta el mensaje como un mensaje JSON para la aplicacion cliente que la haya invocado. En caso de suceder esto
devuelve un JSON con el siguiente formato: 

<pre> 
	{
		"success":"False",
		"msg":"Mensaje explicando el error"
	}
</pre>  

El el WEB METHOD devuelve un 422. 

En caso que el token ha sido creado exitosamente se devuelve un mensaje JSON con los mismos datos que proporsiono y con una etiqueta en particular llamada token el 
cual representa el ID del token que esta alojado en la BBDD. A los efectos de brindar una calidad de servicios aceptable se ha establecedio que la BBDD donse se alojan
los tokens es REDIs la cual es una base de datos en memoria Cache. De esta forma lo unico que se le brinda a la capa de presentacion es un ID que contiene todos los datos del token.

En cada request que envie el cliente debe enviar dentro del header "Authorization" el codigo del token que se ha sumuinistrado en el proceso de creacion del token. 
En caso que se invoque un servicio determinado sin la correponsdiente credencial se espera un mensaje como: 

<pre> 
{
  "msg": "Lo sentimos pero debe indicar el token para acceder a los servicios o bien su token ha caducado", 
  "success": false
}

</pre>

En conclusion: Una vez creado el token siempre debe ser enviado EN TODOS LOS REQUEST que viajen al server sin excepcion alguna. 

Cuando el request llega al server es capturado SIEMPRE por la capa de seguridad quien tomando el token id (clave) verifica que el mismo exista en redis y luego realiza un conjunto de validaciones referentes al token (ej. que el token no este vencido o el mismo corresponda a la IP quien inicia la peticion, etc)

# Dependencias 

* Redis server ejecutandose y accesible 
 
