// Adapter for the installed 32-bit Java Access Bridge. No mouse/OCR input.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading;
using System.Web.Script.Serialization;
using System.Windows.Forms;

public static class JavaBridgeHost
{
    const string Dll = "WindowsAccessBridge-32.dll";
    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
    internal struct ContextInfo
    {
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 1024)] public string name;
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 1024)] public string description;
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 256)] public string role;
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 256)] public string role_en_US;
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 256)] public string states;
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 256)] public string states_en_US;
        public int indexInParent, childrenCount, x, y, width, height;
        public int accessibleComponent, accessibleAction, accessibleSelection, accessibleText, accessibleInterfaces;
    }
    [DllImport(Dll, CallingConvention = CallingConvention.Cdecl)] static extern void Windows_run();
    [DllImport(Dll, CallingConvention = CallingConvention.Cdecl)] static extern bool isJavaWindow(IntPtr hwnd);
    [DllImport(Dll, CallingConvention = CallingConvention.Cdecl)] static extern bool getAccessibleContextFromHWND(IntPtr hwnd, out int vm, out long context);
    [DllImport(Dll, CallingConvention = CallingConvention.Cdecl)] static extern bool getAccessibleContextInfo(int vm, long context, out ContextInfo info);
    [DllImport(Dll, CallingConvention = CallingConvention.Cdecl)] static extern long getAccessibleChildFromContext(int vm, long context, int index);
    [DllImport(Dll, CallingConvention = CallingConvention.Cdecl)] static extern void releaseJavaObject(int vm, long context);
    [DllImport(Dll, CallingConvention = CallingConvention.Cdecl)] static extern bool getAccessibleActions(int vm, long context, IntPtr actions);
    [DllImport(Dll, CallingConvention = CallingConvention.Cdecl)] static extern bool doAccessibleActions(int vm, long context, IntPtr actions, out int failure);
    [DllImport(Dll, CallingConvention = CallingConvention.Cdecl, CharSet = CharSet.Unicode)] static extern bool setTextContents(int vm, long context, string value);
    [DllImport("user32.dll")] static extern bool EnumWindows(EnumWindow callback, IntPtr param);
    [DllImport("user32.dll")] static extern bool IsWindowVisible(IntPtr hwnd);
    [DllImport("user32.dll")] static extern uint GetWindowThreadProcessId(IntPtr hwnd, out uint pid);
    [DllImport("user32.dll", CharSet = CharSet.Unicode)] static extern int GetWindowText(IntPtr hwnd, StringBuilder title, int size);
    delegate bool EnumWindow(IntPtr hwnd, IntPtr param);

    internal sealed class BridgeError : Exception
    {
        public readonly string Code;
        public BridgeError(string code, string message) : base(message) { Code = code; }
    }
    internal sealed class Node
    {
        public long Context;
        public ContextInfo Info;
        public string Path;
    }
    internal sealed class WindowTree : IDisposable
    {
        public long Hwnd;
        public uint Pid;
        public int Vm;
        public string Title;
        public List<Node> Nodes = new List<Node>();
        public void Dispose() { foreach (var node in Nodes) releaseJavaObject(Vm, node.Context); }
    }
    static void Pump(int milliseconds)
    {
        var clock = Stopwatch.StartNew();
        do { Application.DoEvents(); Thread.Sleep(20); } while (clock.ElapsedMilliseconds < milliseconds);
    }
    static void Walk(WindowTree tree, long context, string path, int depth)
    {
        ContextInfo info;
        if (!getAccessibleContextInfo(tree.Vm, context, out info))
        {
            releaseJavaObject(tree.Vm, context);
            return;
        }
        tree.Nodes.Add(new Node { Context = context, Info = info, Path = path });
        if (depth >= 40 || info.role_en_US == "table" || info.role_en_US == "list") return;
        if (tree.Nodes.Count >= 1500) throw new BridgeError("ARVORE_EXCESSIVA", "A interface excedeu o limite de inspeção do Bridge.");
        for (int i = 0; i < info.childrenCount; i++)
        {
            long child = getAccessibleChildFromContext(tree.Vm, context, i);
            if (child != 0) Walk(tree, child, path + "/" + i, depth + 1);
        }
    }
    static List<WindowTree> Windows()
    {
        var result = new List<WindowTree>();
        EnumWindows(delegate(IntPtr hwnd, IntPtr unused) {
            if (!IsWindowVisible(hwnd) || !isJavaWindow(hwnd)) return true;
            int vm; long root;
            if (!getAccessibleContextFromHWND(hwnd, out vm, out root)) return true;
            var title = new StringBuilder(1024);
            GetWindowText(hwnd, title, title.Capacity);
            uint pid; GetWindowThreadProcessId(hwnd, out pid);
            var tree = new WindowTree { Hwnd = hwnd.ToInt64(), Pid = pid, Vm = vm, Title = title.ToString() };
            result.Add(tree);
            try { Walk(tree, root, "0", 0); }
            catch { foreach (var item in result) item.Dispose(); throw; }
            return true;
        }, IntPtr.Zero);
        return result;
    }
    static string Normalize(string value)
    {
        string plain = (value ?? "").Normalize(NormalizationForm.FormD);
        return new string(plain.Where(c => System.Globalization.CharUnicodeInfo.GetUnicodeCategory(c) != System.Globalization.UnicodeCategory.NonSpacingMark).ToArray()).ToLowerInvariant().Trim();
    }
    static bool Ready(Node node) { return (node.Info.states_en_US ?? "").Split(',').Contains("showing") && (node.Info.states_en_US ?? "").Split(',').Contains("enabled"); }
    static Node Unique(IEnumerable<Node> nodes, string label)
    {
        var choices = nodes.ToList();
        if (choices.Count != 1) throw new BridgeError("CONTROLE_NAO_IDENTIFICADO", "Esperado um controle " + label + "; encontrados: " + choices.Count + ".");
        return choices[0];
    }
    static void Act(WindowTree tree, Node node)
    {
        ContextInfo current;
        if (!getAccessibleContextInfo(tree.Vm, node.Context, out current)) throw new BridgeError("CONTROLE_DESAPARECEU", "O controle deixou de estar disponível.");
        node.Info = current;
        IntPtr available = Marshal.AllocHGlobal(4 + 256 * 512);
        IntPtr todo = Marshal.AllocHGlobal(4 + 32 * 512);
        try
        {
            if (!Ready(node) || !getAccessibleActions(tree.Vm, node.Context, available)) throw new BridgeError("ACAO_INDISPONIVEL", "O controle não oferece uma ação acessível habilitada.");
            int count = Marshal.ReadInt32(available);
            if (count < 0 || count > 256) throw new BridgeError("ACOES_INVALIDAS", "A lista de ações retornada pelo Bridge é inválida.");
            var actions = new List<string>();
            for (int i = 0; i < count; i++)
            {
                string name = Marshal.PtrToStringUni(IntPtr.Add(available, 4 + i * 512));
                if (Normalize(name) == "clicar" || Normalize(name) == "click") actions.Add(name);
            }
            if (actions.Count != 1) throw new BridgeError("ACAO_NAO_IDENTIFICADA", "Não foi identificada uma ação de clique única no controle.");
            Marshal.Copy(new byte[4 + 32 * 512], 0, todo, 4 + 32 * 512);
            Marshal.WriteInt32(todo, 1);
            byte[] nameBytes = Encoding.Unicode.GetBytes(actions[0] + "\0");
            Marshal.Copy(nameBytes, 0, IntPtr.Add(todo, 4), nameBytes.Length);
            int failure;
            if (!doAccessibleActions(tree.Vm, node.Context, todo, out failure)) throw new BridgeError("ACAO_FALHOU", "O Bridge não conseguiu executar a ação do controle.");
        }
        finally { Marshal.FreeHGlobal(available); Marshal.FreeHGlobal(todo); }
        Pump(200);
    }
    static bool IsLogin(WindowTree tree) { return Normalize(tree.Title).Contains("i-global"); }
    static object Warning(int timeout)
    {
        var clock = Stopwatch.StartNew();
        while (clock.Elapsed.TotalSeconds < timeout)
        {
            var windows = Windows();
            try
            {
                var warnings = windows.Where(w => Normalize(w.Title) == "advertencia de seguranca").ToList();
                if (warnings.Count > 1) throw new BridgeError("JANELA_AMBIGUA", "Há mais de uma advertência Java aberta.");
                if (warnings.Count == 1)
                {
                    var tree = warnings[0];
                    if (!tree.Nodes.Any(n => n.Info.name == "MenuEglobal.AppEglobal") ||
                        !tree.Nodes.Any(n => n.Info.name == "http://107.21.0.176:8190"))
                        throw new BridgeError("APLICACAO_JAVA_INESPERADA", "A advertência pertence a uma aplicação diferente do launcher iBroker configurado.");
                    var checkbox = Unique(tree.Nodes.Where(n => n.Info.role_en_US == "check box" && Normalize(n.Info.name) == "eu aceito o risco e desejo executar este aplicativo." && Ready(n)), "de aceite Java");
                    if (!(checkbox.Info.states_en_US ?? "").Split(',').Contains("checked")) Act(tree, checkbox);
                    ContextInfo accepted;
                    if (!getAccessibleContextInfo(tree.Vm, checkbox.Context, out accepted) || !(accepted.states_en_US ?? "").Split(',').Contains("checked"))
                        throw new BridgeError("ACEITE_JAVA_FALHOU", "Não foi possível confirmar o checkbox da advertência Java.");
                    Act(tree, Unique(tree.Nodes.Where(n => n.Info.role_en_US == "push button" && Normalize(n.Info.name) == "executar"), "Executar"));
                    return new { ok = true, status = "warning" };
                }
                if (windows.Any(IsLogin)) return new { ok = true, status = "login" };
            }
            finally { foreach (var window in windows) window.Dispose(); }
            Pump(250);
        }
        throw new BridgeError("ABERTURA_JAVA_TIMEOUT", "Nem a advertência Java nem a janela de login apareceram dentro do prazo.");
    }
    static object Login(Dictionary<string, object> request, int timeout)
    {
        string user = (string)request["usuario"];
        string password = (string)request["senha"];
        if (String.IsNullOrWhiteSpace(user) || String.IsNullOrEmpty(password) || user.Length > 1023 || password.Length > 1023)
            throw new BridgeError("CREDENCIAIS_INVALIDAS", "Usuário ou senha ausentes ou excedendo o limite do Bridge.");
        uint selectedPid = 0;
        bool submitted = false;
        var clock = Stopwatch.StartNew();
        while (clock.Elapsed.TotalSeconds < timeout)
        {
            var windows = Windows();
            try
            {
                if (!submitted)
                {
                    var logins = windows.Where(w => IsLogin(w) && Normalize(w.Title).Contains("i-broker export")).ToList();
                    if (logins.Count > 1) throw new BridgeError("LOGIN_AMBIGUO", "Há mais de uma janela de login iBroker aberta.");
                    if (logins.Count == 1)
                    {
                        var tree = logins[0];
                        if (!tree.Nodes.Any(n => n.Info.role_en_US == "label" && Normalize(n.Info.name) == "usuario" && Ready(n)) ||
                            !tree.Nodes.Any(n => n.Info.role_en_US == "label" && Normalize(n.Info.name) == "senha" && Ready(n)))
                            throw new BridgeError("TELA_LOGIN_INESPERADA", "A janela não contém os rótulos de usuário e senha esperados.");
                        var userField = Unique(tree.Nodes.Where(n => n.Info.role_en_US == "text" && Ready(n) && (n.Info.states_en_US ?? "").Split(',').Contains("editable")), "de usuário editável");
                        var passwordField = Unique(tree.Nodes.Where(n => n.Info.role_en_US == "password text" && Ready(n) && (n.Info.states_en_US ?? "").Split(',').Contains("editable")), "de senha editável");
                        var loginButton = Unique(tree.Nodes.Where(n => n.Info.role_en_US == "push button" && Normalize(n.Info.name) == "login" && Ready(n)), "Login");
                        if (!setTextContents(tree.Vm, userField.Context, user)) throw new BridgeError("USUARIO_NAO_PREENCHIDO", "O Bridge não conseguiu preencher o usuário.");
                        if (!setTextContents(tree.Vm, passwordField.Context, password)) throw new BridgeError("SENHA_NAO_PREENCHIDA", "O Bridge não conseguiu preencher a senha.");
                        selectedPid = tree.Pid;
                        Act(tree, loginButton);
                        submitted = true;
                    }
                }
                else
                {
                    var session = windows.Where(w => w.Pid == selectedPid).ToList();
                    var main = session.Where(w => Normalize(w.Title).StartsWith("i-broker export") && Normalize(w.Title).Contains("usuario:")).ToList();
                    if (main.Count == 1 && !session.Any(IsLogin) &&
                        !session.Any(w => w.Nodes.Count > 0 && (w.Nodes[0].Info.states_en_US ?? "").Split(',').Contains("modal")) &&
                        main[0].Nodes.Any(n => n.Info.role_en_US == "menu" && Normalize(n.Info.name) == "tabelas" && Ready(n)) &&
                        main[0].Nodes.Any(n => n.Info.role_en_US == "menu" && Normalize(n.Info.name) == "movimentacao" && Ready(n)))
                    {
                        if (main[0].Nodes.Any(n => n.Info.role_en_US == "internal frame" && !String.IsNullOrWhiteSpace(n.Info.name) && Ready(n)))
                            throw new BridgeError("TELA_INICIAL_NAO_LIVRE", "O login terminou, mas uma tela interna está aberta; a sessão não foi alterada.");
                        return new { ok = true, status = "ready", hwnd = main[0].Hwnd, pid = selectedPid, title = main[0].Title };
                    }
                    if (session.Any(w => !IsLogin(w) && w.Nodes.Count > 0 && (w.Nodes[0].Info.states_en_US ?? "").Split(',').Contains("modal")))
                        throw new BridgeError("LOGIN_BLOQUEADO", "O sistema exibiu uma mensagem bloqueante após a tentativa de login.");
                }
            }
            finally { foreach (var window in windows) window.Dispose(); }
            Pump(250);
        }
        throw new BridgeError(submitted ? "LOGIN_NAO_CONFIRMADO" : "LOGIN_TIMEOUT", submitted ? "A tentativa foi enviada, mas a autenticação e a tela inicial não foram confirmadas dentro do prazo." : "A janela de login não apareceu dentro do prazo.");
    }
    static object Inspect()
    {
        var windows = Windows();
        try
        {
            return new { ok = true, windows = windows.Select(w => new {
                hwnd = w.Hwnd, pid = w.Pid, title = w.Title,
                controls = w.Nodes.Select(n => new { path = n.Path, role = n.Info.role_en_US,
                    name = n.Info.role_en_US == "password text" ? "[senha]" : n.Info.name,
                    description = n.Info.role_en_US == "password text" ? "" : n.Info.description,
                    states = n.Info.states_en_US, action = n.Info.accessibleAction != 0,
                    text = n.Info.accessibleText != 0 }).ToArray()
            }).ToArray() };
        }
        finally { foreach (var window in windows) window.Dispose(); }
    }
    public static int Run(string input)
    {
        Console.InputEncoding = new UTF8Encoding(false);
        Console.OutputEncoding = new UTF8Encoding(false);
        var json = new JavaScriptSerializer { MaxJsonLength = 4000000 };
        try
        {
            var request = json.Deserialize<Dictionary<string, object>>(input);
            Windows_run();
            Pump(800);
            string command = (string)request["command"];
            int timeout = Convert.ToInt32(request["timeout"]);
            object response;
            if (command == "inspect") response = Inspect();
            else if (command == "warning") response = Warning(timeout);
            else if (command == "login") response = Login(request, timeout);
            else throw new BridgeError("COMANDO_INVALIDO", "Comando Bridge não implementado.");
            Console.WriteLine(json.Serialize(response));
            return 0;
        }
        catch (BridgeError error) { Console.WriteLine(json.Serialize(new { ok = false, code = error.Code, message = error.Message })); return 1; }
        catch (Exception error) { Console.WriteLine(json.Serialize(new { ok = false, code = "BRIDGE_INDISPONIVEL", message = "Falha ao inicializar/comunicar com o Java Access Bridge: " + error.GetType().Name })); return 1; }
    }
}
