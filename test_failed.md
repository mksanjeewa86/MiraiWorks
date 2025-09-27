
======================================================================= ERRORS ========================================================================
__________________________________________________ ERROR at setup of test_admin_can_list_candidates ___________________________________________________
file C:\Users\mksan\OneDrive\ドキュメント\projects\MiraiWorks\backend\app\tests\test_candidate_workflows.py, line 29
  @pytest.mark.asyncio
  async def test_admin_can_list_candidates(
      client: AsyncClient,
      admin_auth_headers: dict,
      db_session: AsyncSession,
      test_roles: dict[str, Role],
      test_admin_user: User,
  ):
      await ensure_role(db_session, test_roles, UserRoleEnum.CANDIDATE)

      candidate = User(
          email="workflow.candidate@example.com",
          first_name="Workflow",
          last_name="Candidate",
          company_id=test_admin_user.company_id,
          hashed_password=auth_service.get_password_hash("candidatepass"),
          is_active=True,
      )
      db_session.add(candidate)
      await db_session.commit()
      await db_session.refresh(candidate)

      db_session.add(
          UserRole(
              user_id=candidate.id, role_id=test_roles[UserRoleEnum.CANDIDATE.value].id
          )
      )
      await db_session.commit()

      response = await client.get(
          "/api/admin/users",
          headers=admin_auth_headers,
          params={"role": "candidate", "size": 100},
      )

      assert response.status_code == 200
      users = response.json()["users"]
      assert any(user["email"] == candidate.email for user in users)
E       fixture 'admin_auth_headers' not found
>       available fixtures: _session_faker, anyio_backend, anyio_backend_name, anyio_backend_options, auth_headers, cache, candidate_headers, capfd, capfdbinary, caplog, capsys, capsysbinary, client, cov, db_session, doctest_namespace, event_loop, faker, monkeypatch, no_cover, pytestconfig, record_property, record_testsuite_property, record_xml_attribute, recwarn, setup_database, setup_database_schema, setup_test_environment, test_admin_user, test_candidate_only_user, test_company, test_employer_user, test_roles, test_user, tmp_path, tmp_path_factory, tmpdir, tmpdir_factory, unused_tcp_port, unused_tcp_port_factory, unused_udp_port, unused_udp_port_factory
>       use 'pytest --fixtures [testpath]' for help on them.

C:\Users\mksan\OneDrive\ドキュメント\projects\MiraiWorks\backend\app\tests\test_candidate_workflows.py:29
_____________________________________________ ERROR at setup of TestCompanies.test_get_companies_success ______________________________________________ 
file C:\Users\mksan\OneDrive\ドキュメント\projects\MiraiWorks\backend\app\tests\test_companies.py, line 16
      @pytest.mark.asyncio
      async def test_get_companies_success(
          self, client: AsyncClient, super_admin_auth_headers: dict
      ):
          """Test successful retrieval of companies list."""
          response = await client.get(
              "/api/admin/companies", headers=super_admin_auth_headers
          )

          assert response.status_code == 200
          data = response.json()
          assert "companies" in data
          assert "total" in data
          assert "page" in data
          assert "size" in data
          assert isinstance(data["companies"], list)
E       fixture 'super_admin_auth_headers' not found
>       available fixtures: _session_faker, anyio_backend, anyio_backend_name, anyio_backend_options, auth_headers, cache, candidate_headers, capfd, capfdbinary, caplog, capsys, capsysbinary, client, cov, db_session, doctest_namespace, event_loop, faker, monkeypatch, no_cover, pytestconfig, record_property, record_testsuite_property, record_xml_attribute, recwarn, setup_database, setup_database_schema, setup_test_environment, test_admin_user, test_candidate_only_user, test_company, test_employer_user, test_roles, test_user, tmp_path, tmp_path_factory, tmpdir, tmpdir_factory, unused_tcp_port, unused_tcp_port_factory, unused_udp_port, unused_udp_port_factory
>       use 'pytest --fixtures [testpath]' for help on them.

C:\Users\mksan\OneDrive\ドキュメント\projects\MiraiWorks\backend\app\tests\test_companies.py:16
_________________________________________ ERROR at setup of TestCompanies.test_get_companies_with_pagination __________________________________________ 
file C:\Users\mksan\OneDrive\ドキュメント\projects\MiraiWorks\backend\app\tests\test_companies.py, line 33
      @pytest.mark.asyncio
      async def test_get_companies_with_pagination(
          self, client: AsyncClient, super_admin_auth_headers: dict
      ):
          """Test companies list with pagination parameters."""
          response = await client.get(
              "/api/admin/companies?page=1&size=10", headers=super_admin_auth_headers
          )

          assert response.status_code == 200
          data = response.json()
          assert data["page"] == 1
          assert data["size"] == 10
E       fixture 'super_admin_auth_headers' not found
>       available fixtures: _session_faker, anyio_backend, anyio_backend_name, anyio_backend_options, auth_headers, cache, candidate_headers, capfd, capfdbinary, caplog, capsys, capsysbinary, client, cov, db_session, doctest_namespace, event_loop, faker, monkeypatch, no_cover, pytestconfig, record_property, record_testsuite_property, record_xml_attribute, recwarn, setup_database, setup_database_schema, setup_test_environment, test_admin_user, test_candidate_only_user, test_company, test_employer_user, test_roles, test_user, tmp_path, tmp_path_factory, tmpdir, tmpdir_factory, unused_tcp_port, unused_tcp_port_factory, unused_udp_port, unused_udp_port_factory
>       use 'pytest --fixtures [testpath]' for help on them.

C:\Users\mksan\OneDrive\ドキュメント\projects\MiraiWorks\backend\app\tests\test_companies.py:33
====================================================================== FAILURES =======================================================================
_________________________________________________ TestAccountActivation.test_activation_success_flow __________________________________________________ 

self = <tests.test_activation_comprehensive.TestAccountActivation object at 0x00000273AFFC2310>
client = <tests.conftest.client.<locals>.PatchedAsyncClient object at 0x00000273B228F110>
db_session = <sqlalchemy.ext.asyncio.session.AsyncSession object at 0x00000273B22F3650>

    async def test_activation_success_flow(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test successful account activation with all required steps."""
        # Create test company
        company = Company(
            name="Test Activation Company",
            email="activation@test.com",
            phone="03-1234-5678",
            type="employer",
        )
        db_session.add(company)
        await db_session.commit()
        await db_session.refresh(company)

        # Create inactive user with temporary password
        temp_password = "TempPass123"
        hashed_password = auth_service.get_password_hash(temp_password)

        user = User(
            email="activate@test.com",
            first_name="Test",
            last_name="User",
            company_id=company.id,
            hashed_password=hashed_password,
            is_active=False,  # Key: user is inactive
            is_admin=False,
            require_2fa=False,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Test activation
        activation_data = {
            "userId": user.id,
            "email": "activate@test.com",
            "temporaryPassword": temp_password,
            "newPassword": "NewSecure@123",
        }

        response = await client.post("/api/auth/activate", json=activation_data)

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert data["success"] is True
        assert data["message"] == "Account activated successfully"
        assert "access_token" in data
        assert "refresh_token" in data
        assert "user" in data

        # Verify user data in response
        user_data = data["user"]
        assert user_data["email"] == "activate@test.com"
        assert user_data["is_active"] is True

        # Verify database changes
        await db_session.refresh(user)
>       assert user.is_active is True
E       AssertionError: assert False is True
E        +  where False = <User(id=1, email='activate@test.com', company_id=1)>.is_active

app\tests\test_activation_comprehensive.py:83: AssertionError
---------------------------------------------------------------- Captured stdout setup ---------------------------------------------------------------- 
Database schema already exists (55 tables)
Starting MySQL test database...
MySQL test database is already running and healthy
Test environment ready - database will persist between test runs
---------------------------------------------------------------- Captured stdout call ----------------------------------------------------------------- 
2025-09-27T00:30:07.854509Z [info     ] Request started                [app.middleware.logging] authenticated=False client_ip=127.0.0.1 component=request method=POST path=/api/auth/activate query_params={} request_id=b8260ea3-a87f-4aac-8e73-f5f1eaf06835 user_agent=python-httpx/0.25.2
2025-09-27T00:30:08.328414Z [info     ] User account activated successfully [app.endpoints.auth] authenticated=False client_ip=127.0.0.1 component=auth email=activate@test.com method=POST path=/api/auth/activate request_id=b8260ea3-a87f-4aac-8e73-f5f1eaf06835 user_id=1
2025-09-27T00:30:08.349543Z [info     ] Request completed              [app.middleware.logging] authenticated=False client_ip=127.0.0.1 component=response duration_ms=495.03 method=POST path=/api/auth/activate request_id=b8260ea3-a87f-4aac-8e73-f5f1eaf06835 status_code=200
HTTP Request: POST http://testserver/api/auth/activate "HTTP/1.1 200 OK"
------------------------------------------------------------------ Captured log call ------------------------------------------------------------------ 
INFO     app.middleware.logging:logging.py:55 2025-09-27T00:30:07.854509Z [info     ] Request started                [app.middleware.logging] authenticated=False client_ip=127.0.0.1 component=request method=POST path=/api/auth/activate query_params={} request_id=b8260ea3-a87f-4aac-8e73-f5f1eaf06835 user_agent=python-httpx/0.25.2
INFO     app.endpoints.auth:auth.py:767 2025-09-27T00:30:08.328414Z [info     ] User account activated successfully [app.endpoints.auth] authenticated=False client_ip=127.0.0.1 component=auth email=activate@test.com method=POST path=/api/auth/activate request_id=b8260ea3-a87f-4aac-8e73-f5f1eaf06835 user_id=1
INFO     app.middleware.logging:logging.py:74 2025-09-27T00:30:08.349543Z [info     ] Request completed              [app.middleware.logging] authenticated=False client_ip=127.0.0.1 component=response duration_ms=495.03 method=POST path=/api/auth/activate request_id=b8260ea3-a87f-4aac-8e73-f5f1eaf06835 status_code=200
INFO     httpx:_client.py:1729 HTTP Request: POST http://testserver/api/auth/activate "HTTP/1.1 200 OK"
_____________________________________________ TestAccountActivation.test_activation_missing_phone_default _____________________________________________ 

self = <tests.test_activation_comprehensive.TestAccountActivation object at 0x00000273B1997F90>
client = <tests.conftest.client.<locals>.PatchedAsyncClient object at 0x00000273B2C6A050>
db_session = <sqlalchemy.ext.asyncio.session.AsyncSession object at 0x00000273B31BDC50>

    async def test_activation_missing_phone_default(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test that default phone number is added during activation."""
        user = User(
            email="phone@test.com",
            first_name="Phone",
            last_name="User",
            hashed_password=auth_service.get_password_hash("TempPass123"),
            phone=None,  # No phone number
            is_active=False,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        activation_data = {
            "userId": user.id,
            "email": "phone@test.com",
            "temporaryPassword": "TempPass123",
            "newPassword": "NewSecure@123",
        }

        response = await client.post("/api/auth/activate", json=activation_data)

        assert response.status_code == 200

        # Verify default phone was added
        await db_session.refresh(user)
>       assert user.phone == "+1-555-0100"
E       AssertionError: assert None == '+1-555-0100'
E        +  where None = <User(id=1, email='phone@test.com', company_id=None)>.phone

app\tests\test_activation_comprehensive.py:422: AssertionError
---------------------------------------------------------------- Captured stdout call ----------------------------------------------------------------- 
2025-09-27T00:30:39.752491Z [info     ] Request started                [app.middleware.logging] authenticated=False client_ip=127.0.0.1 component=request method=POST path=/api/auth/activate query_params={} request_id=a1f97f3c-3ced-48ca-8456-db087c5ea4f0 user_agent=python-httpx/0.25.2
2025-09-27T00:30:40.194572Z [info     ] User account activated successfully [app.endpoints.auth] authenticated=False client_ip=127.0.0.1 component=auth email=phone@test.com method=POST path=/api/auth/activate request_id=a1f97f3c-3ced-48ca-8456-db087c5ea4f0 user_id=1
2025-09-27T00:30:40.207149Z [info     ] Request completed              [app.middleware.logging] authenticated=False client_ip=127.0.0.1 component=response duration_ms=454.66 method=POST path=/api/auth/activate request_id=a1f97f3c-3ced-48ca-8456-db087c5ea4f0 status_code=200
HTTP Request: POST http://testserver/api/auth/activate "HTTP/1.1 200 OK"
------------------------------------------------------------------ Captured log call ------------------------------------------------------------------ 
INFO     app.middleware.logging:logging.py:55 2025-09-27T00:30:39.752491Z [info     ] Request started                [app.middleware.logging] authenticated=False client_ip=127.0.0.1 component=request method=POST path=/api/auth/activate query_params={} request_id=a1f97f3c-3ced-48ca-8456-db087c5ea4f0 user_agent=python-httpx/0.25.2
INFO     app.endpoints.auth:auth.py:767 2025-09-27T00:30:40.194572Z [info     ] User account activated successfully [app.endpoints.auth] authenticated=False client_ip=127.0.0.1 component=auth email=phone@test.com method=POST path=/api/auth/activate request_id=a1f97f3c-3ced-48ca-8456-db087c5ea4f0 user_id=1
INFO     app.middleware.logging:logging.py:74 2025-09-27T00:30:40.207149Z [info     ] Request completed              [app.middleware.logging] authenticated=False client_ip=127.0.0.1 component=response duration_ms=454.66 method=POST path=/api/auth/activate request_id=a1f97f3c-3ced-48ca-8456-db087c5ea4f0 status_code=200
INFO     httpx:_client.py:1729 HTTP Request: POST http://testserver/api/auth/activate "HTTP/1.1 200 OK"
=============================================================== short test summary info =============================================================== 
FAILED app/tests/test_activation_comprehensive.py::TestAccountActivation::test_activation_success_flow - AssertionError: assert False is True
FAILED app/tests/test_activation_comprehensive.py::TestAccountActivation::test_activation_missing_phone_default - AssertionError: assert None == '+1-555-0100'
ERROR app/tests/test_candidate_workflows.py::test_admin_can_list_candidates
ERROR app/tests/test_companies.py::TestCompanies::test_get_companies_success
ERROR app/tests/test_companies.py::TestCompanies::test_get_companies_with_pagination
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 5 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 
================================================= 2 failed, 41 passed, 3 errors in 148.05s (0:02:28) ================================================== 
[FAILED] Failed in 152.17s
PS C:\Users\mksan\OneDrive\ドキュメント\projects\MiraiWorks\backend>