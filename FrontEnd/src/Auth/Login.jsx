const Login = () => {
  const submit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch("http://localhost:8080/v1/auth", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: e.target[0].value,
          password: e.target[1].value,
        }),
      });
      const data = await response.json();
      if (data?.email) {
        localStorage.setItem("user", JSON.stringify({ email: data.email }));
        window.location.href = `/${data.email}`;
      }
    } catch (error) {
      console.log(error);
    }
  };
  return (
    <div className="flex bg-black h-screen flex-col justify-start items-center gap-5 p-10 w-full text-white">
      <h1>Login</h1>
      <div className="flex justify-center items-center">
        <form onSubmit={submit} className="flex flex-col gap-4">
          <input type="email" className="input" placeholder="Email" />
          <input type="password" className="input" placeholder="password" />
          <input type="submit" value="submit" className="btn-l" />
        </form>
      </div>
    </div>
  );
};

export default Login;
