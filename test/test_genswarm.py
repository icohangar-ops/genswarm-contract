"""
GenSwarm Integration Tests
Tests for the Stigmergic Agent Coordination Protocol contract.

Run with: gltest
Requires: GenLayer Studio running
"""

import unittest
import json
import os
import requests
from dotenv import load_dotenv
from genlayer_test.contracts import ContractWrapper

load_dotenv()


def get_config() -> dict:
    """Read RPC config from environment."""
    return {
        "rpc_protocol": os.environ["RPCPROTOCOL"],
        "rpc_host": os.environ["RPCHOST"],
        "rpc_port": os.environ["RPCPORT"],
    }


class TestGenSwarm(unittest.TestCase):
    """Test suite for the GenSwarm Intelligent Contract."""

    @classmethod
    def setUpClass(cls):
        """Deploy contract once for all tests."""
        config = get_config()
        cls.rpc_url = f"{config['rpc_protocol']}://{config['rpc_host']}:{config['rpc_port']}"
        cls.wrapper = ContractWrapper(cls.rpc_url, "contracts/genswarm.py")

        print("\n=== Deploying GenSwarm Contract ===")
        cls.contract_address = cls.wrapper.deploy()
        print(f"Contract deployed at: {cls.contract_address}")

        # Store for other tests to use
        cls.registered_workers = []

    def _get_account(self, index: int = 0) -> str:
        """Get test account address."""
        # Standard test account from GenLayer Studio
        accounts = [
            "0xa1b2C3D4e5F60718293a4B5c6D7E8f9A0b1C2d3E",
            "0xb2C3D4e5F60718293a4B5c6D7E8f9A0b1C2d3E4F",
            "0xC3D4e5F60718293a4B5c6D7E8f9A0b1C2d3E4F5a6",
        ]
        return accounts[index % len(accounts)]

    def test_01_register_worker(self):
        """Test worker registration."""
        print("\n--- Test: Register Worker ---")
        addr = self._get_account(0)
        result = self.wrapper.call(
            self.contract_address,
            "register_worker",
            addr,
            [
                "worker-alice",
                json.dumps(["financial", "analyst", "trading"]),
                "deepseek-r1",
            ],
        )
        print(f"Result: {result}")
        self.registered_workers.append(addr)

        # Verify registration
        worker_info = self.wrapper.call(
            self.contract_address,
            "get_worker",
            addr,
            [addr],
        )
        print(f"Worker info: {worker_info}")
        self.assertIsNotNone(worker_info)

    def test_02_register_second_worker(self):
        """Test second worker with different skills."""
        print("\n--- Test: Register Second Worker ---")
        addr = self._get_account(1)
        result = self.wrapper.call(
            self.contract_address,
            "register_worker",
            addr,
            [
                "worker-bob",
                json.dumps(["cybersecurity", "threat-hunting", "soc"]),
                "qwen-2.5",
            ],
        )
        print(f"Result: {result}")
        self.registered_workers.append(addr)

    def test_03_submit_job(self):
        """Test job submission with AI decomposition."""
        print("\n--- Test: Submit Job ---")
        addr = self._get_account(0)
        result = self.wrapper.call(
            self.contract_address,
            "submit_job",
            addr,
            [
                "job-market-analysis",
                "Analyze the top 10 tech stocks by market cap and provide a buy/sell/hold recommendation for each based on current financial metrics, recent news sentiment, and technical indicators.",
                "financial",
                10000,
            ],
        )
        print(f"Job submitted: {result}")

        # Verify job was created and decomposed
        job_info = self.wrapper.call(
            self.contract_address,
            "get_job",
            addr,
            ["job-market-analysis"],
        )
        print(f"Job info: {job_info}")
        self.assertIsNotNone(job_info)

    def test_04_get_pending_tasks(self):
        """Test viewing pending tasks."""
        print("\n--- Test: Get Pending Tasks ---")
        addr = self._get_account(0)
        tasks = self.wrapper.call(
            self.contract_address,
            "get_pending_tasks",
            addr,
            [],
        )
        print(f"Pending tasks: {tasks}")
        self.assertIsInstance(tasks, list)

    def test_05_get_scent_field(self):
        """Test reading scent field signals."""
        print("\n--- Test: Get Scent Field ---")
        addr = self._get_account(0)

        # Get pending tasks first
        tasks = self.wrapper.call(
            self.contract_address,
            "get_pending_tasks",
            addr,
            [],
        )

        if tasks and len(tasks) > 0:
            task_id = tasks[0]["task_id"]
            scent = self.wrapper.call(
                self.contract_address,
                "get_scent_field",
                addr,
                [task_id],
            )
            print(f"Scent field for {task_id}: {scent}")
            self.assertIn("scents", scent)

    def test_06_swarm_stats(self):
        """Test swarm statistics."""
        print("\n--- Test: Swarm Stats ---")
        addr = self._get_account(0)
        stats = self.wrapper.call(
            self.contract_address,
            "get_swarm_stats",
            addr,
            [],
        )
        print(f"Swarm stats: {stats}")
        self.assertIn("total_tasks", stats)
        self.assertIn("total_workers", stats)

    def test_07_leaderboard(self):
        """Test leaderboard."""
        print("\n--- Test: Leaderboard ---")
        addr = self._get_account(0)
        board = self.wrapper.call(
            self.contract_address,
            "get_leaderboard",
            addr,
            [],
        )
        print(f"Leaderboard: {board}")
        self.assertIsInstance(board, list)

    def test_08_all_jobs(self):
        """Test getting all jobs."""
        print("\n--- Test: All Jobs ---")
        addr = self._get_account(0)
        jobs = self.wrapper.call(
            self.contract_address,
            "get_all_jobs",
            addr,
            [],
        )
        print(f"All jobs: {jobs}")
        self.assertIsInstance(jobs, list)


if __name__ == "__main__":
    unittest.main()
