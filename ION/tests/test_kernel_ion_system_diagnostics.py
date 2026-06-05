from pathlib import Path

from kernel import ion_system_diagnostics as diagnostics


def test_nested_cosmos_workspace_wins_over_ion_root(tmp_path: Path):
    ion_root = tmp_path / "ION_Developement"
    cwd = ion_root / "Cosmos" / "StudioEARTH"
    cwd.mkdir(parents=True)
    cockpit_cwd = ion_root / "ION" / "04_packages"
    cockpit_cwd.mkdir(parents=True)

    assert diagnostics._classify_workspace(cwd.as_posix(), "") == "Cosmos"
    assert diagnostics._protected_process(4242, "node vite --host 127.0.0.1", cwd.as_posix(), ion_root) is False
    assert diagnostics._protected_process(4243, "python3 -m kernel.ion_local_cockpit_app", cockpit_cwd.as_posix(), ion_root) is True
    assert diagnostics._dev_server("node ./node_modules/.bin/vite --host 127.0.0.1", cwd.as_posix(), ion_root) is True


def test_protected_project_dev_server_is_visible_but_not_cleanup(monkeypatch):
    process = {
        "pid": 5179,
        "name": "node",
        "command": "node ./node_modules/.bin/vite --host 127.0.0.1",
        "cwd": "/home/sev/ION - Production/ION_Developement/Cosmos/sailboat/source/latest",
        "workspace": "Cosmos",
        "protected": True,
        "dev_server": True,
        "dev_server_reason": "vite_command",
        "framework": "vite",
        "package_name": "sailboat-viewer",
        "package_path": "/home/sev/ION - Production/ION_Developement/Cosmos/sailboat/source/latest/package.json",
        "elapsed_seconds": 7200,
        "cpu_percent": 0.1,
        "rss_kb": 256000,
    }
    port = {
        "protocol": "tcp",
        "local_address": "127.0.0.1",
        "port": 5179,
        "pid": 5179,
        "process_name": "node",
        "command": process["command"],
        "cwd": process["cwd"],
        "workspace": "Cosmos",
        "dev_server": True,
        "dev_server_reason": "vite_command",
        "framework": "vite",
        "package_name": "sailboat-viewer",
        "package_path": process["package_path"],
        "protected": True,
        "cleanup_candidate": False,
    }

    monkeypatch.setattr(
        diagnostics,
        "_probe_http_port",
        lambda _: {"serves_http": True, "url": "http://127.0.0.1:5179/", "http_status": 200, "finding": "ok", "title": "Sailboat"},
    )

    rows = diagnostics._dev_servers([port], [process])

    assert rows == [
        {
            "id": "5179:5179",
            "port": 5179,
            "pid": 5179,
            "process_name": "node",
            "workspace": "Cosmos",
            "cwd": process["cwd"],
            "command": process["command"],
            "elapsed_seconds": 7200,
            "cpu_percent": 0.1,
            "rss_kb": 256000,
            "protected": True,
            "dev_server": True,
            "cleanup_candidate": False,
            "stale": False,
            "framework": "vite",
            "package_name": "sailboat-viewer",
            "package_path": process["package_path"],
            "reason": "vite_command",
            "confidence": "high",
            "http_probe": {"serves_http": True, "url": "http://127.0.0.1:5179/", "http_status": 200, "finding": "ok", "title": "Sailboat"},
            "action": {"action_type": "stop_process", "target_pid": 5179, "target_port": 5179},
        }
    ]


def test_cosmos_project_dev_server_is_cleanup_candidate(monkeypatch):
    process = {
        "pid": 6210,
        "name": "node",
        "command": "node ./node_modules/.bin/vite --host 127.0.0.1",
        "cwd": "/home/sev/ION - Production/ION_Developement/Cosmos/example-app",
        "workspace": "Cosmos",
        "protected": False,
        "dev_server": True,
        "dev_server_reason": "vite_command",
        "framework": "vite",
        "package_name": "example-app",
        "package_path": "/home/sev/ION - Production/ION_Developement/Cosmos/example-app/package.json",
        "elapsed_seconds": 8 * 3600,
        "cpu_percent": 0.2,
        "rss_kb": 128000,
    }
    port = {
        "protocol": "tcp",
        "local_address": "127.0.0.1",
        "port": 5178,
        "pid": 6210,
        "process_name": "node",
        "command": process["command"],
        "cwd": process["cwd"],
        "workspace": "Cosmos",
        "dev_server": True,
        "dev_server_reason": "vite_command",
        "framework": "vite",
        "package_name": "example-app",
        "package_path": process["package_path"],
        "protected": False,
        "cleanup_candidate": True,
    }

    monkeypatch.setattr(
        diagnostics,
        "_probe_http_port",
        lambda _: {"serves_http": True, "url": "http://127.0.0.1:5178/", "http_status": 200, "finding": "ok", "title": "Example"},
    )

    dev_servers = diagnostics._dev_servers([port], [process])
    cleanup_candidates = diagnostics._cleanup_candidates([port], [process])

    assert dev_servers[0]["cleanup_candidate"] is True
    assert dev_servers[0]["protected"] is False
    assert cleanup_candidates == [
        {
            "id": "6210:5178",
            "pid": 6210,
            "port": 5178,
            "process_name": "node",
            "workspace": "Cosmos",
            "cwd": process["cwd"],
            "elapsed_seconds": 8 * 3600,
            "cpu_percent": 0.2,
            "stale": True,
            "action": {"action_type": "stop_process", "target_pid": 6210, "target_port": 5178},
        }
    ]


def test_system_diagnostics_model_includes_dev_server_inventory(monkeypatch, tmp_path: Path):
    process = {
        "pid": 3231,
        "ppid": 1,
        "state": "S",
        "elapsed_seconds": 120,
        "cpu_percent": 1.0,
        "memory_percent": 1.0,
        "rss_kb": 512000,
        "command": "next-server (v16.2.6)",
        "name": "next-server",
        "cwd": "/home/sev/ION - Production/ION_Developement/Cosmos/hyperh2o",
        "workspace": "Cosmos",
        "protected": True,
        "dev_server": True,
        "dev_server_reason": "next_command",
        "framework": "next",
        "package_name": "hyperh2o",
        "package_path": "/home/sev/ION - Production/ION_Developement/Cosmos/hyperh2o/package.json",
    }
    port = {
        "protocol": "tcp",
        "local_address": "127.0.0.1",
        "port": 3231,
        "pid": 3231,
        "process_name": "next-server",
        "command": process["command"],
        "cwd": process["cwd"],
        "workspace": "Cosmos",
        "dev_server": True,
        "dev_server_reason": "next_command",
        "framework": "next",
        "package_name": "hyperh2o",
        "package_path": process["package_path"],
        "protected": True,
        "cleanup_candidate": False,
    }

    monkeypatch.setattr(diagnostics, "collect_processes", lambda _: [process])
    monkeypatch.setattr(diagnostics, "collect_ports", lambda _processes, _root: [port])
    monkeypatch.setattr(diagnostics, "_mem_info", lambda: {"MemTotal": 1024 * 1024, "MemAvailable": 768 * 1024, "SwapTotal": 1024, "SwapFree": 1024})
    monkeypatch.setattr(diagnostics, "_cpu_percent", lambda: 12.0)
    monkeypatch.setattr(diagnostics, "_disk_percent", lambda: 40.0)
    monkeypatch.setattr(diagnostics, "_load_avg", lambda: [1.0, 1.0, 1.0])
    monkeypatch.setattr(diagnostics, "_uptime_seconds", lambda: 500)
    monkeypatch.setattr(
        diagnostics,
        "_probe_http_port",
        lambda _: {"serves_http": True, "url": "http://127.0.0.1:3231/", "http_status": 200, "finding": "ok", "title": "HyperH2O"},
    )

    model = diagnostics.build_system_diagnostics_model(tmp_path)

    assert model["summary"]["active_dev_server_count"] == 1
    assert model["summary"]["protected_dev_server_count"] == 1
    assert model["summary"]["http_verified_dev_server_count"] == 1
    assert model["summary"]["cleanup_candidate_count"] == 0
    assert model["dev_servers"][0]["port"] == 3231
    assert model["dev_servers"][0]["protected"] is True
    assert model["data_quality"]["dev_server_count_includes_protected"] is True
    assert model["data_quality"]["cleanup_candidates_exclude_protected"] is True


def test_unresponsive_dev_server_becomes_diagnostics_issue():
    issues = diagnostics._detect_dev_server_issues(
        [
            {
                "port": 3231,
                "pid": 99,
                "dev_server": True,
                "cleanup_candidate": False,
                "package_name": "hyperh2o",
                "cwd": "/home/sev/ION - Production/ION_Developement/Cosmos/hyperh2o",
                "http_probe": {"serves_http": False, "finding": "TimeoutError", "url": "http://127.0.0.1:3231/"},
                "action": {"action_type": "stop_process", "target_pid": 99, "target_port": 3231},
            }
        ]
    )

    assert issues[0]["id"] == "dev-server-http-probe-3231"
    assert "not HTTP responsive" in issues[0]["title"]
    assert issues[0]["action"] is None
